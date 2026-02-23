"""
Database models for the application.
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
    gender = Column(String(1))  # М или Ж
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
    file_type = Column(String(50))  # pdf, docx, txt
    file_size = Column(Integer)  # in bytes
    extracted_text = Column(Text)  # Extracted content
    extracted_skills = Column(JSON)  # {"hard_skills": [...], "soft_skills": [...]}
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")


class Analysis(Base):
    """Analysis model for PGD calculations and AI reports."""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # PGD Calculation Results
    pgd_data = Column(JSON)  # Full PGD matrix
    
    # AI Analysis
    ai_analysis = Column(Text)  # Full career analysis from Gemini
    career_tracks = Column(JSON)  # Recommended career paths
    
    # Skills Assessment
    soft_skills_score = Column(Float)  # 0-100
    hard_skills_score = Column(Float)  # 0-100
    skills_breakdown = Column(JSON)  # Detailed skills analysis
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
