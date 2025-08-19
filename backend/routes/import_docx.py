from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import shutil
import logging
from ..services.docx_parser import DocxParser
from ..models.question import Question
from ..models.subject import Subject
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import", tags=["Import DOCX"])

class ImportResponse(BaseModel):
    success: bool
    message: str
    total_questions: int = 0
    imported_questions: int = 0
    errors: List[str] = []
    questions: List[Dict[str, Any]] = []

@router.post("/docx", response_model=ImportResponse)
async def import_docx(
    file: UploadFile = File(...),
    subject_id: int = Form(...),
    created_by: int = Form(...)
):
    """Import DOCX file vào database"""
    try:
        # Validate file
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="File must be a DOCX file")
        
        # Create upload directory if not exists
        os.makedirs(settings.get_upload_dir(), exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(settings.get_upload_dir(), file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse DOCX
        parser = DocxParser()
        questions_data = parser.parse_docx(file_path)
        
        # Validate questions
        validation = parser.validate_questions()
        
        if not validation['valid']:
            return ImportResponse(
                success=False,
                message="Validation failed",
                errors=validation['errors'],
                total_questions=validation['total_questions']
            )
        
        # Import questions to database
        imported_count = 0
        errors = []
        
        for question_data in questions_data:
            try:
                logger.info(f"Importing question {question_data['question_number']}: {question_data['question_text']}")
                
                # Convert choices to database format
                choices = []
                for choice in question_data['choices']:
                    choices.append({
                        'content': choice['content'],
                        'is_correct': choice['is_correct']
                    })
                
                logger.info(f"Choices: {choices}")
                
                # Create question
                question = Question.create(
                    subject_id=subject_id,
                    unit_text=question_data['unit'],
                    question=question_data['question_text'],
                    mix_choices=1 if question_data['mix_choices'] else 0,
                    image=question_data['image'],
                    mark=question_data['mark'],
                    created_by=created_by,
                    choices=choices
                )
                
                if question:
                    imported_count += 1
                    logger.info(f"Successfully imported question {question_data['question_number']}")
                else:
                    error_msg = f"Failed to import question {question_data['question_number']}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Error importing question {question_data['question_number']}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return ImportResponse(
            success=imported_count > 0,
            message=f"Imported {imported_count} out of {len(questions_data)} questions",
            total_questions=len(questions_data),
            imported_questions=imported_count,
            errors=errors,
            questions=questions_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview")
async def preview_docx(file: UploadFile = File(...)):
    """Preview DOCX file trước khi import"""
    try:
        # Validate file
        if not file.filename.endswith('.docx'):
            raise HTTPException(status_code=400, detail="File must be a DOCX file")
        
        # Create upload directory if not exists
        os.makedirs(settings.get_upload_dir(), exist_ok=True)
        
        # Save uploaded file temporarily
        file_path = os.path.join(settings.get_upload_dir(), f"preview_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse DOCX
        parser = DocxParser()
        questions_data = parser.parse_docx(file_path)
        
        # Validate questions
        validation = parser.validate_questions()
        
        # Clean up temporary file
        os.remove(file_path)
        
        return {
            "success": True,
            "total_questions": len(questions_data),
            "valid": validation['valid'],
            "errors": validation['errors'],
            "warnings": validation['warnings'],
            "questions": questions_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 