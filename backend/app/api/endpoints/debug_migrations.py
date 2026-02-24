from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.post("/fix-analyses-columns")
async def fix_analyses_columns(
    db: AsyncSession = Depends(get_db),
):
    """
    Однократный фикс схемы таблицы analyses на Render.
    Добавляет недостающие колонки, если их нет.
    """
    queries = [
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS client_name VARCHAR",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS client_date_of_birth VARCHAR",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS client_gender VARCHAR",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS client_document_id INTEGER",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS pgd_data JSON",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS insights TEXT",
        "ALTER TABLE analyses ADD COLUMN IF NOT EXISTS recommendations TEXT",
    ]
    for q in queries:
        await db.execute(text(q))
    await db.commit()
    return {"status": "ok"}
