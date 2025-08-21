from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from ..models.question import Question, Choice
from ..models.user import User
from ..middleware.auth import require_auth, optional_auth, require_subject_access, get_user_subjects_filter

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
    request: Request,
    subject_id: Optional[int] = Query(None),
    current_user: User = Depends(optional_auth)
):
    """Lấy tất cả questions, có thể filter theo subject"""
    try:
        # Nếu không có user đăng nhập, trả về tất cả câu hỏi
        if not current_user:
            questions = Question.get_all(subject_id)
            return [QuestionResponse(**question.to_dict()) for question in questions]
        
        # Kiểm tra quyền truy cập môn học
        if subject_id:
            require_subject_access(request, subject_id)
        else:
            # Nếu không filter theo subject, chỉ trả về môn học user có quyền
            allowed_subjects = get_user_subjects_filter(request)
            if allowed_subjects:
                questions = []
                for subj_id in allowed_subjects:
                    subj_questions = Question.get_all(subj_id)
                    questions.extend(subj_questions)
                return [QuestionResponse(**question.to_dict()) for question in questions]
        
        questions = Question.get_all(subject_id)
        return [QuestionResponse(**question.to_dict()) for question in questions]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting questions: {e}")
        # Cung cấp thông báo lỗi cụ thể hơn
        if "connection" in str(e).lower() or "database" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection error. Please try again later.")
        elif "permission" in str(e).lower():
            raise HTTPException(status_code=403, detail="Permission denied. You don't have access to this resource.")
        else:
            raise HTTPException(status_code=500, detail="An error occurred while loading questions. Please try again.")

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    request: Request,
    current_user: User = Depends(optional_auth)
):
    """Lấy question theo ID"""
    try:
        question = Question.get_by_id(question_id)
        if question:
            # Nếu có user đăng nhập, kiểm tra quyền truy cập môn học
            if current_user:
                require_subject_access(request, question.subject_id)
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
async def create_question(
    request: CreateQuestionRequest,
    req: Request,
    current_user: User = Depends(require_auth)
):
    """Tạo question mới"""
    try:
        # Kiểm tra quyền truy cập môn học
        require_subject_access(req, request.subject_id)
        
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
async def update_question(
    question_id: int, 
    request: CreateQuestionRequest,
    req: Request,
    current_user: User = Depends(require_auth)
):
    """Cập nhật question"""
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Updating question {question_id}")
        
        question = Question.get_by_id(question_id)
        if not question:
            logger.error(f"Question {question_id} not found")
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Kiểm tra quyền truy cập môn học
        require_subject_access(req, question.subject_id)
        
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
async def delete_question(
    question_id: int,
    req: Request,
    current_user: User = Depends(require_auth)
):
    """Xóa question"""
    try:
        question = Question.get_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Kiểm tra quyền truy cập môn học
        require_subject_access(req, question.subject_id)
        
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