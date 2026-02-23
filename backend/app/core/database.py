"""
Database configuration and session management.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings


def make_async_url(url: str) -> str:
    """
    Преобразует URL от Render / .env к async-формату для SQLAlchemy.
    Примеры:
    - postgres://...        -> postgresql+asyncpg://...
    - postgresql://...      -> postgresql+asyncpg://...
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


ASYNC_DATABASE_URL = make_async_url(settings.DATABASE_URL)

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
