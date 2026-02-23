"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.endpoints import auth, documents, analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS origins
# settings.BACKEND_CORS_ORIGINS обычно List[str] или строка с JSON/CSV — приводим к списку строк
origins: List[str] = []

if isinstance(settings.BACKEND_CORS_ORIGINS, (list, tuple)):
    origins = [str(o) for o in settings.BACKEND_CORS_ORIGINS]
elif isinstance(settings.BACKEND_CORS_ORIGINS, str) and settings.BACKEND_CORS_ORIGINS:
    # например, '["https://foo"]' или 'https://foo,https://bar'
    if settings.BACKEND_CORS_ORIGINS.strip().startswith("["):
        # JSON-список
        import json

        origins = [str(o) for o in json.loads(settings.BACKEND_CORS_ORIGINS)]
    else:
        # CSV-строка
        origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",") if o.strip()]

# На всякий случай можно добавить локальный фронт для разработки
if "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Career Intelligence Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
