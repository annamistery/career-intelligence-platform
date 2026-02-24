"""
Career analysis endpoints.

ИСПРАВЛЕНИЯ:
1. PGDCalculator() → PGDCalculator() с вызовом calculator.calculate(...)
   (конструктор без аргументов теперь допустим — см. pgd_service.py)

2. ai_service.generate_analysis() теперь реально существует в ai_service.py
   и возвращает AIAnalysisResult с .insights и .recommendations.

3. AnalysisResponse.from_orm() → AnalysisResponse.model_validate()
   from_orm() — устаревший Pydantic v1 API, в Pydantic v2 вызывает AttributeError.

4. Дублирующий импорт `from typing import List` перенесён наверх.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.models import User, Analysis, Document
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    PGDCalculationRequest,
    PGDCalculationResponse,
)

from app.services.pgd_service import PGDCalculator
from app.services.ai_service import AIAnalysisService

router = APIRouter(prefix="/analysis", tags=["Career Analysis"])


@router.post("/pgd", response_model=PGDCalculationResponse)
async def calculate_pgd(
    payload: PGDCalculationRequest,
) -> PGDCalculationResponse:
    """
    Calculate PGD numbers for given date of birth.
    """
    # BUG FIX: PGDCalculator() — без обязательных аргументов (исправлено в pgd_service.py)
    calculator = PGDCalculator()
    result = calculator.calculate(
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
    )
    return result


@router.post("/independent", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def independent_analysis(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """
    Create analysis based only on name + date of birth (+ optional client_document_id).
    """
    document: Document | None = None
    if payload.client_document_id is not None:
        result = await db.execute(
            select(Document).where(
                Document.id == payload.client_document_id,
                Document.user_id == current_user.id,
            )
        )
        document = result.scalar_one_or_none()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

    ai_service = AIAnalysisService()
    # BUG FIX: PGDCalculator() без аргументов
    calculator = PGDCalculator()

    # Calculate PGD
    pgd_result = calculator.calculate(
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
    )

    # BUG FIX: вызов generate_analysis() (добавлен в ai_service.py),
    # который возвращает AIAnalysisResult с полями .insights и .recommendations.
    # В оригинале: метод не существовал → AttributeError при запросе.
    ai_result = await ai_service.generate_analysis(
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        pgd_result=pgd_result,
        resume_text=document.extracted_text if document else None,
    )

    analysis = Analysis(
        user_id=current_user.id,
        client_name=payload.name,
        client_date_of_birth=payload.date_of_birth,
        client_gender=payload.gender,
        pgd_data=pgd_result,
        insights=ai_result.insights,
        recommendations=ai_result.recommendations,
        client_document_id=document.id if document else None,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # BUG FIX: from_orm() → model_validate()
    # from_orm() — Pydantic v1, вызывает AttributeError в Pydantic v2
    return AnalysisResponse.model_validate(analysis)


@router.post("/create", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    payload: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """
    Create analysis for a client based on PGD + resume (required document).
    """
    if payload.client_document_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="client_document_id is required for this endpoint",
        )

    result = await db.execute(
        select(Document).where(
            Document.id == payload.client_document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    ai_service = AIAnalysisService()
    # BUG FIX: PGDCalculator() без аргументов
    calculator = PGDCalculator()

    # Calculate PGD
    pgd_result = calculator.calculate(
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
    )

    # BUG FIX: generate_analysis() вместо несуществующего метода
    ai_result = await ai_service.generate_analysis(
        name=payload.name,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        pgd_result=pgd_result,
        resume_text=document.extracted_text,
    )

    analysis = Analysis(
        user_id=current_user.id,
        client_name=payload.name,
        client_date_of_birth=payload.date_of_birth,
        client_gender=payload.gender,
        pgd_data=pgd_result,
        insights=ai_result.insights,
        recommendations=ai_result.recommendations,
        client_document_id=document.id,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # BUG FIX: from_orm() → model_validate()
    return AnalysisResponse.model_validate(analysis)


@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[AnalysisResponse]:
    """List analyses of the current user (history)."""
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
    )
    analyses: List[Analysis] = result.scalars().all()
    # BUG FIX: from_orm() → model_validate()
    return [AnalysisResponse.model_validate(a) for a in analyses]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalysisResponse:
    """Get a single analysis by id, only for the owner."""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    # BUG FIX: from_orm() → model_validate()
    return AnalysisResponse.model_validate(analysis)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a single analysis of the current user."""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found",
        )

    await db.delete(analysis)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_analyses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete all analyses of the current user (clear history)."""
    await db.execute(
        delete(Analysis).where(Analysis.user_id == current_user.id)
    )
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
