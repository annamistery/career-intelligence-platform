"""
Document upload and management endpoints.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pathlib import Path
from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.models.models import User, Document
from app.models.schemas import DocumentUploadResponse
from app.services.document_service import DocumentProcessor

router = APIRouter(prefix="/documents", tags=["Documents"])

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document (resume) for analysis.
    
    Args:
        file: Uploaded file
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Document metadata with extracted skills
        
    Raises:
        HTTPException: If file type is invalid or processing fails
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower().replace('.', '')
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Create user-specific directory
    user_upload_dir = Path(settings.UPLOAD_DIR) / str(current_user.id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = user_upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Process document
        extracted_text, extracted_skills = DocumentProcessor.process_document(
            str(file_path), file_extension
        )
        
        # Save to database
        new_document = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_path=str(file_path),
            file_type=file_extension,
            file_size=file_size,
            extracted_text=extracted_text,
            extracted_skills=extracted_skills
        )
        
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)
        
        return DocumentUploadResponse.model_validate(new_document)
        
    except Exception as e:
        # Clean up file if processing fails
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/", response_model=List[DocumentUploadResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all documents uploaded by current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of user's documents
    """
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()
    
    return [DocumentUploadResponse.model_validate(doc) for doc in documents]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document.
    
    Args:
        document_id: ID of document to delete
        current_user: Authenticated user
        db: Database session
        
    Raises:
        HTTPException: If document not found or unauthorized
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file from disk
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    await db.delete(document)
    await db.commit()
