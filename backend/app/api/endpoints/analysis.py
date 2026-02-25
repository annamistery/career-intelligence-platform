"""
Career analysis endpoints.

ИЗМЕНЕНИЯ В ЭТОЙ ВЕРСИИ:
1.  Унифицированы эндпоинты POST /independent и POST /create в один - POST /.
2.  Добавлена новая Pydantic-модель AnalysisCreateRequest с флагами include_pgd
    и include_resume для гибкого выбора типа анализа.
3.  Эндпоинт теперь передает флаги use_pgd и use_resume в AI-сервис,
    активируя логику раздельного или совместного анализа.
4.  Сохранены все исправления из предыдущих версий (Pydantic v2, async вызовы).
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, Field, root_validator
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.models import User, Analysis, Document
from app.models.schemas import (
    AnalysisResponse,
    PGDCalculationRequest,
    PGDCalculationResponse,
)
from app.services.pgd_service import PGDCalculator
from app.services.ai_service import AIAnalysisService

router = APIRouter(prefix="/analysis", tags=["Career Analysis"])


# ### НОВАЯ МОДЕЛЬ ЗАПРОСА ДЛЯ СОЗДАНИЯ АНАЛИЗА ###
class AnalysisCreateRequest(BaseModel):
    """Модель для создания нового анализа с гибким выбором источников."""
    name: str = Field(..., description="Имя клиента для анализа")
    date_of_birth: str = Field(..., description="Дата рождения клиента (DD.MM.YYYY)")
    gender: str = Field(..., description="Пол клиента (М/Ж)")

    include_pgd: bool = Field(True, description="Включить в анализ данные PGD-матрицы")
    include_resume: bool = Field(False, description="Включить в анализ данные из резюме")
    
    client_document_id: Optional[int] = Field(None, description="ID документа с резюме (обязателен, если include_resume=True)")

    @root_validator
    def check_dependencies(cls, values):
        """Проверяет, что document_id передан, если запрошен анализ по резюме."""
        include_resume, doc_id = values.get("include_resume"), values.get("client_document_id")
        if include_resume and doc_id is None:
            raise ValueError("client_document_id является обязательным, если include_resume=True.")
        if not values.get("include_pgd") and not include_resume:
            raise ValueError("Должен быть выбран хотя бы один источник анализа: PGD или резюме.")
        return values


# --- Существующие эндпоинты ---

@router.post("/pgd", response_model=PGDCalculationResponse)
async def calculate_pgd(payload: PGDCalculationRequest) -> PGDCalculationResponse:
    """
    Рассчитывает данные PGD-матрицы для указанной даты рождения.
    """
    calculator = PGDCalculator()
    result = calculator.calculate(date_of_birth=payload.date_of_birth, gender=payload.gender)
    return result


# ### ОБЪЕДИНЕННЫЙ ЭНДПОИНТ СОЗДАНИЯ АНАЛИЗА ###
@router.post("/", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    payload: AnalysisCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AIAnalysisService = Depends(),
) -> AnalysisResponse:
    """
    Создает новый карьерный анализ на основе выбранных данных (PGD и/или резюме).
    """
    pgd_data = None
    if payload.include_pgd:
        calculator = PGDCalculator()
        pgd_data = calculator.calculate(date_of_birth=payload.date_of_birth, gender=payload.gender)

    resume_text = None
    document = None
    if payload.include_resume:
        result = await db.execute(
            select(Document).where(
                Document.id == payload.client_document_id,
                Document.user_id == current_user.id
            )
        )
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Документ с id={payload.client_document_id} не найден или не принадлежит вам.",
            )
        resume_text = document.extracted_text

    try:
        ai_result = await ai_service.generate_analysis(
            name=payload.name,
            date_of_birth=payload.date_of_birth,
            gender=payload.gender,
            pgd_result=pgd_data,
            resume_text=resume_text,
            use_pgd=payload.include_pgd,
            use_resume=payload.include_resume,
        )
    except ValueError as e:
        # Отлавливаем ошибки валидации из сервиса
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Сохранение результатов в базу данных
    new_analysis = Analysis(
        user_id=current_user.id,
        client_name=payload.name,
        client_date_of_birth=payload.date_of_birth,
        client_gender=payload.gender,
        pgd_data=pgd_data,  # Сохраняем Pydantic-объект, SQLAlchemy обработает его
        insights=ai_result.insights,
        recommendations=ai_result.recommendations,
        client_document_id=document.id if document else None,
    )

    db.add(new_analysis)
    await db.commit()
    await db.refresh(new_analysis)

    return AnalysisResponse.model_validate(new_analysis)


@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[AnalysisResponse]:
    """Возвращает историю анализов текущего пользователя."""
    result = await db.execute(
        select(Analysis).where(Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc())
    )
    analyses: List[Analysis] = result.scalars().all()
    return [AnalysisResponse.model_validate(a) for a in analyses]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """Возвращает один анализ по id (только для владельца)."""
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Анализ не найден.")
    return AnalysisResponse.model_validate(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Удаляет один анализ текущего пользователя."""
    result = await db.execute(
        delete(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == current_user.id).returning(Analysis.id)
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Анализ не найден.")
    
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_analyses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Удаляет всю историю анализов текущего пользователя."""
    await db.execute(delete(Analysis).where(Analysis.user_id == current_user.id))
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
