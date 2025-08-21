from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..models.question import Question, Choice

router = APIRouter(prefix="/questions", tags=["Questions"])

class ChoiceResponse(BaseModel):
    id: int
    question_id: int
    content: str
    is_correct: bool
    position: int
    created_at: str

class QuestionResponse(BaseModel):
    id: int
    subject_id: int
    unit_text: Optional[str]
    question: str
    mix_choices: int
    image: Optional[str]
    mark: float
    created_by: int
    created_at: str
    updated_by: Optional[int]
    updated_at: Optional[str] = None
    choices: List[ChoiceResponse]

class CreateQuestionRequest(BaseModel):
    subject_id: int
    unit_text: Optional[str]
    question: str
    mix_choices: int = 1
    image: Optional[str] = None
    mark: float = 1.0
    created_by: int
    choices: List[dict]

@router.get("/", response_model=List[QuestionResponse])
async def get_questions(subject_id: Optional[int] = Query(None)):
    """Lấy tất cả questions, có thể filter theo subject"""
    try:
        questions = Question.get_all(subject_id)
        return [QuestionResponse(**question.to_dict()) for question in questions]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting questions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load questions: {str(e)}")

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int):
    """Lấy question theo ID"""
    try:
        question = Question.get_by_id(question_id)
        if question:
            return QuestionResponse(**question.to_dict())
        else:
            raise HTTPException(status_code=404, detail="Question not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=QuestionResponse)
async def create_question(request: CreateQuestionRequest):
    """Tạo question mới"""
    try:
        question = Question.create(
            subject_id=request.subject_id,
            unit_text=request.unit_text,
            question=request.question,
            mix_choices=request.mix_choices,
            image=request.image,
            mark=request.mark,
            created_by=request.created_by,
            choices=request.choices
        )
        if question:
            return QuestionResponse(**question.to_dict())
        else:
            raise HTTPException(status_code=400, detail="Failed to create question")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{question_id}")
async def update_question(question_id: int, request: CreateQuestionRequest):
    """Cập nhật question"""
    try:
        question = Question.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        success = question.update(
            unit_text=request.unit_text,
            question=request.question,
            mix_choices=request.mix_choices,
            image=request.image,
            mark=request.mark,
            updated_by=request.created_by,
            choices=request.choices
        )
        
        if success:
            updated_question = Question.get_by_id(question_id)
            return QuestionResponse(**updated_question.to_dict())
        else:
            raise HTTPException(status_code=400, detail="Failed to update question")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{question_id}")
async def delete_question(question_id: int):
    """Xóa question"""
    try:
        question = Question.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        success = question.delete()
        if success:
            return {"success": True, "message": "Question deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete question")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 