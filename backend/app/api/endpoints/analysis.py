"""
Career analysis endpoints - PGD calculations and AI-powered recommendations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.models import User, Analysis, Document
from app.models.schemas import (
    AnalysisRequest, AnalysisResponse, AnalysisListResponse,
    PGDCalculationRequest, PGDCalculationResponse,
    SkillsBreakdown, CareerTrack
)
from app.services.pgd_service import PGDCalculator
from app.services.ai_service import AIAnalysisService

router = APIRouter(prefix="/analysis", tags=["Career Analysis"])


@router.post("/pgd", response_model=PGDCalculationResponse)
async def calculate_pgd(
    data: PGDCalculationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate PGD (Psychographic Diagnosis) matrix without saving to database.
    
    Args:
        data: PGD calculation input data
        current_user: Authenticated user
        
    Returns:
        PGD calculation results
    """
    try:
        calculator = PGDCalculator(data.name, data.date_of_birth, data.gender)
        result = calculator.get_full_analysis()
        
        return PGDCalculationResponse(
            main_cup=result['main_cup'],
            ancestral_data=result['ancestral_data'],
            crossroads=result['crossroads'],
            tasks=result.get('tasks'),
            business_periods=result.get('business_periods')
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/create", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a comprehensive career analysis using PGD + AI + document analysis.
    
    Args:
        request: Analysis creation parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete career analysis with recommendations
        
    Raises:
        HTTPException: If user profile is incomplete or analysis fails
    """
    # Validate user has complete profile
    if not all([current_user.full_name, current_user.date_of_birth, current_user.gender]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete your profile (name, date of birth, gender) before creating analysis"
        )
    
    try:
        # Step 1: Calculate PGD matrix
        calculator = PGDCalculator(
            current_user.full_name,
            current_user.date_of_birth,
            current_user.gender
        )
        pgd_data = calculator.get_full_analysis()
        
        # Step 2: Get user's documents if requested
        document_text = None
        extracted_skills = None
        
        if request.include_documents:
            result = await db.execute(
                select(Document)
                .where(Document.user_id == current_user.id)
                .order_by(Document.uploaded_at.desc())
                .limit(1)
            )
            latest_document = result.scalar_one_or_none()
            
            if latest_document:
                document_text = latest_document.extracted_text
                extracted_skills = latest_document.extracted_skills
        
        # Step 3: Generate AI analysis
        ai_service = AIAnalysisService()
        
        user_data = {
            "full_name": current_user.full_name,
            "date_of_birth": current_user.date_of_birth,
            "gender": current_user.gender
        }
        
        analysis_text = await ai_service.generate_career_analysis(
            user_data=user_data,
            pgd_data=pgd_data,
            document_text=document_text,
            extracted_skills=extracted_skills
        )
        
        # Step 4: Parse structured data from analysis
        structured_data = ai_service.parse_analysis_for_structured_data(analysis_text)
        
        # Step 5: Calculate skills breakdown
        soft_skills = extracted_skills.get('soft_skills', []) if extracted_skills else []
        hard_skills = extracted_skills.get('hard_skills', []) if extracted_skills else []
        
        soft_score = structured_data.get('soft_skills_score', 50.0)
        hard_score = structured_data.get('hard_skills_score', 50.0)
        
        total = soft_score + hard_score
        soft_percent = int((soft_score / total) * 100) if total > 0 else 50
        hard_percent = 100 - soft_percent
        
        skills_breakdown_data = {
            "soft_skills": soft_skills,
            "hard_skills": hard_skills,
            "soft_skills_score": soft_score,
            "hard_skills_score": hard_score,
            "balance_ratio": f"{soft_percent}/{hard_percent}"
        }
        
        # Step 6: Save analysis to database
        new_analysis = Analysis(
            user_id=current_user.id,
            pgd_data=pgd_data,
            ai_analysis=analysis_text,
            career_tracks=structured_data.get('career_tracks', []),
            soft_skills_score=soft_score,
            hard_skills_score=hard_score,
            skills_breakdown=skills_breakdown_data
        )
        
        db.add(new_analysis)
        await db.commit()
        await db.refresh(new_analysis)
        
        # Step 7: Format response
        career_tracks = [CareerTrack(**track) for track in structured_data.get('career_tracks', [])]
        skills_breakdown = SkillsBreakdown(**skills_breakdown_data)
        
        return AnalysisResponse(
            id=new_analysis.id,
            pgd_data=new_analysis.pgd_data,
            ai_analysis=new_analysis.ai_analysis,
            career_tracks=career_tracks,
            skills_breakdown=skills_breakdown,
            created_at=new_analysis.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create analysis: {str(e)}"
        )


@router.get("/", response_model=List[AnalysisListResponse])
async def list_analyses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all analyses for current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of user's analyses
    """
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
    )
    analyses = result.scalars().all()
    
    return [
        AnalysisListResponse(
            id=analysis.id,
            created_at=analysis.created_at,
            career_tracks_count=len(analysis.career_tracks) if analysis.career_tracks else 0
        )
        for analysis in analyses
    ]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed analysis by ID.
    
    Args:
        analysis_id: ID of analysis
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Complete analysis data
        
    Raises:
        HTTPException: If analysis not found or unauthorized
    """
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        )
    )
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    career_tracks = [CareerTrack(**track) for track in (analysis.career_tracks or [])]
    skills_breakdown = SkillsBreakdown(**analysis.skills_breakdown) if analysis.skills_breakdown else None
    
    return AnalysisResponse(
        id=analysis.id,
        pgd_data=analysis.pgd_data,
        ai_analysis=analysis.ai_analysis,
        career_tracks=career_tracks,
        skills_breakdown=skills_breakdown,
        created_at=analysis.created_at
    )
