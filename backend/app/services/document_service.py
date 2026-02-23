"""
Document processing service for extracting text and skills from resumes.
"""
import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import PyPDF2
import docx
import pdfplumber


class DocumentProcessor:
    """Service for processing uploaded documents (resumes)."""
    
    # Common hard skills keywords (can be extended)
    HARD_SKILLS_KEYWORDS = [
        # Programming languages
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
        "php", "swift", "kotlin", "scala", "r", "matlab",
        
        # Frameworks & Libraries
        "react", "vue", "angular", "django", "flask", "fastapi", "spring", "node.js",
        "express", "laravel", "rails", ".net", "tensorflow", "pytorch", "keras",
        
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle",
        "cassandra", "dynamodb", "sqlite",
        
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab", "github",
        "terraform", "ansible", "ci/cd", "linux", "bash",
        
        # Data & Analytics
        "excel", "power bi", "tableau", "data analysis", "machine learning", "deep learning",
        "nlp", "computer vision", "data science", "statistics", "pandas", "numpy",
        
        # Design & Creative
        "photoshop", "illustrator", "figma", "sketch", "adobe xd", "indesign",
        "premiere pro", "after effects", "blender", "3d modeling",
        
        # Business & Management
        "project management", "agile", "scrum", "jira", "confluence", "crm", "erp",
        "sap", "salesforce", "hubspot", "ms office", "google workspace",
        
        # Other technical
        "api", "rest", "graphql", "microservices", "testing", "qa", "selenium",
        "git", "version control", "networking", "security", "encryption"
    ]
    
    # Soft skills keywords
    SOFT_SKILLS_KEYWORDS = [
        "leadership", "communication", "teamwork", "problem solving", "critical thinking",
        "creativity", "adaptability", "time management", "emotional intelligence",
        "collaboration", "interpersonal", "presentation", "negotiation", "conflict resolution",
        "decision making", "strategic thinking", "innovation", "mentoring", "coaching",
        "empathy", "active listening", "persuasion", "networking", "work ethic",
        "attention to detail", "organization", "multitasking", "stress management",
        "customer service", "public speaking", "writing", "analytical", "self-motivated"
    ]
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        
        # Try with pdfplumber first (better for complex PDFs)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"PyPDF2 also failed: {e}")
                raise ValueError(f"Could not extract text from PDF: {e}")
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text content
        """
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Could not extract text from DOCX: {e}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from TXT file.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['cp1251', 'latin-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read().strip()
                except:
                    continue
            raise ValueError("Could not decode text file with any known encoding")
    
    @classmethod
    def extract_text(cls, file_path: str, file_type: str) -> str:
        """
        Extract text from document based on file type.
        
        Args:
            file_path: Path to document
            file_type: File extension (pdf, docx, txt)
            
        Returns:
            Extracted text content
        """
        file_type = file_type.lower().replace('.', '')
        
        if file_type == 'pdf':
            return cls.extract_text_from_pdf(file_path)
        elif file_type in ['docx', 'doc']:
            return cls.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return cls.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @classmethod
    def extract_skills(cls, text: str) -> Dict[str, List[str]]:
        """
        Extract hard and soft skills from text using keyword matching.
        
        Args:
            text: Document text content
            
        Returns:
            Dictionary with hard_skills and soft_skills lists
        """
        text_lower = text.lower()
        
        # Extract hard skills
        hard_skills = []
        for skill in cls.HARD_SKILLS_KEYWORDS:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                hard_skills.append(skill.title())
        
        # Extract soft skills
        soft_skills = []
        for skill in cls.SOFT_SKILLS_KEYWORDS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                soft_skills.append(skill.title())
        
        # Remove duplicates and sort
        hard_skills = sorted(list(set(hard_skills)))
        soft_skills = sorted(list(set(soft_skills)))
        
        return {
            "hard_skills": hard_skills,
            "soft_skills": soft_skills
        }
    
    @classmethod
    def process_document(cls, file_path: str, file_type: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Process document: extract text and skills.
        
        Args:
            file_path: Path to document
            file_type: File extension
            
        Returns:
            Tuple of (extracted_text, extracted_skills)
        """
        # Extract text
        text = cls.extract_text(file_path, file_type)
        
        # Extract skills
        skills = cls.extract_skills(text)
        
        return text, skills
