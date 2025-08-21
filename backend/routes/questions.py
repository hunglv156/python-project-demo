from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..models.question import Question, Choice
from ..models.user_subject import UserSubject

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
async def get_questions(
    subject_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None)
):
    """Lấy questions theo subject_id và user_id"""
    try:
        if user_id:
            # Lấy môn học được phân công cho user
            user_subject_ids = UserSubject.get_user_subjects(user_id)
            
            if not user_subject_ids:
                # User không có môn học được phân công (như importer), trả về tất cả
                questions = Question.get_all(subject_id)
                return [QuestionResponse(**question.to_dict()) for question in questions]
            
            if subject_id:
                # Kiểm tra user có quyền truy cập môn học này không
                if subject_id not in user_subject_ids:
                    raise HTTPException(status_code=403, detail="Môn học này không thuộc bạn quản lý")
                # Lấy câu hỏi của môn học cụ thể
                questions = Question.get_all(subject_id)
            else:
                # Lấy câu hỏi của tất cả môn học được phân công
                questions = []
                for subj_id in user_subject_ids:
                    subj_questions = Question.get_all(subj_id)
                    questions.extend(subj_questions)
        else:
            # Không có user_id thì trả về tất cả
            questions = Question.get_all(subject_id)
        
        return [QuestionResponse(**question.to_dict()) for question in questions]
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting questions: {e}")
        # Cung cấp thông báo lỗi cụ thể hơn
        if "connection" in str(e).lower() or "database" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection error. Please try again later.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while loading questions. Please try again.")

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
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting question {question_id}: {e}")
        if "connection" in str(e).lower() or "database" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection error. Please try again later.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while loading the question. Please try again.")

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
            raise HTTPException(status_code=400, detail="Failed to create question. Please check your input data.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating question: {e}")
        if "connection" in str(e).lower() or "database" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection error. Please try again later.")
        elif "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=409, detail="A question with similar content already exists.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while creating the question. Please try again.")

@router.put("/{question_id}")
async def update_question(question_id: int, request: CreateQuestionRequest):
    """Cập nhật question"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Updating question {question_id}")
        
        question = Question.get_by_id(question_id)
        if not question:
            logger.error(f"Question {question_id} not found")
            raise HTTPException(status_code=404, detail="Question not found")
        
        logger.info(f"Found question {question_id}, updating...")
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
            logger.info(f"Question {question_id} updated successfully")
            # Trả về question đã được update (không cần gọi lại get_by_id)
            return QuestionResponse(**question.to_dict())
        else:
            logger.error(f"Failed to update question {question_id}")
            raise HTTPException(status_code=400, detail="Failed to update question. Please check your input data.")
    except ValueError as e:
        logger.error(f"Validation error updating question {question_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating question {question_id}: {e}")
        if "connection" in str(e).lower() or "database" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection error. Please try again later.")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Question not found or has been deleted.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while updating the question. Please try again.")

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
            raise HTTPException(status_code=400, detail="Failed to delete question. The question may be in use by an exam.")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting question {question_id}: {e}")
        if "connection" in str(e).lower() or "database" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection error. Please try again later.")
        elif "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="Cannot delete question. It is being used by an exam.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while deleting the question. Please try again.") 