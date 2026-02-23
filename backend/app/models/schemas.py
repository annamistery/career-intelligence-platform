"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)
    date_of_birth: str = Field(..., pattern=r'^\d{2}\.\d{2}\.\d{4}$')
    gender: str = Field(..., pattern=r'^[МЖ]$')
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format DD.MM.YYYY."""
        from datetime import datetime
        try:
            datetime.strptime(v, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Date must be in DD.MM.YYYY format')
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============= Document Schemas =============

class DocumentUploadResponse(BaseModel):
    """Schema for document upload response."""
    id: int
    filename: str
    file_type: str
    file_size: int
    extracted_skills: Optional[Dict[str, List[str]]] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ============= PGD Schemas =============

class PGDCalculationRequest(BaseModel):
    """Schema for PGD calculation request."""
    name: str
    date_of_birth: str = Field(..., pattern=r'^\d{2}\.\d{2}\.\d{4}$')
    gender: str = Field(..., pattern=r'^[МЖ]$')


class PGDPoint(BaseModel):
    """Schema for a single PGD point."""
    name: str
    value: int
    description: Optional[str] = None


class PGDCalculationResponse(BaseModel):
    """Schema for PGD calculation response."""
    main_cup: Dict[str, int]
    ancestral_data: Dict[str, int]
    crossroads: Dict[str, int]
    tasks: Optional[Dict[str, Optional[int]]] = None
    business_periods: Optional[Dict[str, Dict[str, Optional[int]]]] = None


# ============= Analysis Schemas =============

class AnalysisRequest(BaseModel):
    """Schema for creating career analysis."""
    include_documents: bool = Field(default=True, description="Include uploaded documents in analysis")


class SkillsBreakdown(BaseModel):
    """Schema for skills breakdown."""
    soft_skills: List[str]
    hard_skills: List[str]
    soft_skills_score: float = Field(..., ge=0, le=100)
    hard_skills_score: float = Field(..., ge=0, le=100)
    balance_ratio: str  # e.g., "60/40" (soft/hard)


class CareerTrack(BaseModel):
    """Schema for career track recommendation."""
    title: str
    description: str
    match_score: float = Field(..., ge=0, le=100)
    key_strengths: List[str]
    development_areas: List[str]


class AnalysisResponse(BaseModel):
    """Schema for analysis response."""
    id: int
    pgd_data: Dict[str, Any]
    ai_analysis: str
    career_tracks: List[CareerTrack]
    skills_breakdown: SkillsBreakdown
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    """Schema for list of analyses."""
    id: int
    created_at: datetime
    career_tracks_count: int
    
    class Config:
        from_attributes = True
