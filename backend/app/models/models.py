"""
Database models for the application.

ИСПРАВЛЕНИЯ:
- Добавлены отсутствующие колонки в модель Analysis:
  client_name, client_date_of_birth, client_gender,
  insights, recommendations, client_document_id
  (без них analysis.py падал при db.commit() — AttributeError / IntegrityError)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """User model for authentication and profile."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    date_of_birth = Column(String(10))  # DD.MM.YYYY format
    gender = Column(String(1))          # М или Ж
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    """Document model for uploaded files (resumes, etc.)."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50))   # pdf, docx, txt
    file_size = Column(Integer)      # in bytes
    extracted_text = Column(Text)    # Extracted content
    extracted_skills = Column(JSON)  # {"hard_skills": [...], "soft_skills": [...]}
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")


class Analysis(Base):
    """Analysis model for PGD calculations and AI reports.

    BUG FIX: добавлены колонки, которые использует analysis.py,
    но которых не было в исходной модели:
      - client_name          (VARCHAR 255)
      - client_date_of_birth (VARCHAR 10)
      - client_gender        (VARCHAR 1)
      - insights             (TEXT  — детальный анализ от ИИ)
      - recommendations      (TEXT  — рекомендации от ИИ)
      - client_document_id   (FK -> documents.id, nullable)
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Поля клиента (были в endpoints, но отсутствовали в модели) ---
    client_name = Column(String(255), nullable=False, default="")
    client_date_of_birth = Column(String(10), nullable=False, default="")
    client_gender = Column(String(1), nullable=False, default="")

    # --- Опциональная привязка к документу ---
    client_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # --- PGD Calculation Results ---
    pgd_data = Column(JSON)   # Full PGD matrix

    # --- AI Analysis (разделено на два поля вместо одного ai_analysis) ---
    insights = Column(Text)        # Глубокий анализ личности
    recommendations = Column(Text) # Рекомендации по развитию карьеры

    # --- Legacy field (оставлен для обратной совместимости) ---
    ai_analysis = Column(Text)

    # --- Career tracks & skills ---
    career_tracks = Column(JSON)        # Recommended career paths
    soft_skills_score = Column(Float)   # 0-100
    hard_skills_score = Column(Float)   # 0-100
    skills_breakdown = Column(JSON)     # Detailed skills analysis

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="analyses")
