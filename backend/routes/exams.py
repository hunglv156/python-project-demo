from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..models.exam import Exam, ExamVersion
from ..models.subject import Subject
from ..models.question import Question
from ..utils.subject_code_generator import generate_subject_code, generate_exam_code, get_next_exam_number
import random
import json

router = APIRouter(prefix="/exams", tags=["Exams"])

class CreateExamRequest(BaseModel):
    subject_id: int
    duration_minutes: int
    num_questions: int
    generated_by: int

class ExamResponse(BaseModel):
    id: int
    subject_id: int
    code: str
    title: str
    duration_minutes: int
    num_questions: int
    generated_by: int
    created_at: str
    subject_name: Optional[str] = None
    versions: List[dict] = []

class ExamPreviewResponse(BaseModel):
    id: int
    code: str
    subject_name: str
    duration_minutes: int
    num_questions: int
    questions: List[dict]

@router.get("/", response_model=List[ExamResponse])
async def get_exams():
    """Lấy tất cả exams"""
    try:
        exams = Exam.get_all()
        return [ExamResponse(**exam.to_dict()) for exam in exams]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: int):
    """Lấy exam theo ID"""
    try:
        exam = Exam.get_by_id(exam_id)
        if exam:
            return ExamResponse(**exam.to_dict())
        else:
            raise HTTPException(status_code=404, detail="Exam not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{exam_id}/preview", response_model=ExamPreviewResponse)
async def get_exam_preview(exam_id: int):
    """Lấy preview đề thi với câu hỏi và đáp án đã xáo"""
    try:
        exam = Exam.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        # Lấy version đầu tiên (hoặc tạo mới nếu chưa có)
        versions = exam.get_versions()
        if not versions:
            raise HTTPException(status_code=404, detail="No exam version found")
        
        version = versions[0]  # Lấy version đầu tiên
        questions_data = version.get_questions_with_shuffled_choices()
        
        # Lấy tên môn học
        subject = Subject.get_by_id(exam.subject_id)
        subject_name = subject.name if subject else "Unknown"
        
        return ExamPreviewResponse(
            id=exam.id,
            code=exam.code,
            subject_name=subject_name,
            duration_minutes=exam.duration_minutes,
            num_questions=exam.num_questions,
            questions=questions_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ExamResponse)
async def create_exam(request: CreateExamRequest):
    """Tạo exam mới với auto generate code và random questions"""
    try:
        print(f"Creating exam with request: {request}")
        
        # Validate subject exists
        subject = Subject.get_by_id(request.subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        print(f"Found subject: {subject.name}")
        
        # Generate subject code
        subject_code = generate_subject_code(subject.name)
        print(f"Generated subject code: {subject_code}")
        
        # Get next exam number
        exam_number = get_next_exam_number(request.subject_id, subject_code)
        print(f"Next exam number: {exam_number}")
        
        # Generate exam code
        exam_code = generate_exam_code(subject_code, exam_number)
        print(f"Generated exam code: {exam_code}")
        
        # Generate title
        exam_title = f"Đề thi {subject.name} - {exam_code}"
        print(f"Generated title: {exam_title}")
        
        # Get random questions from subject
        questions = Question.get_all(subject_id=request.subject_id)
        print(f"Found {len(questions)} questions for subject")
        
        if len(questions) < request.num_questions:
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough questions. Available: {len(questions)}, Requested: {request.num_questions}"
            )
        
        # Randomly select questions
        selected_questions = random.sample(questions, request.num_questions)
        question_ids = [q.id for q in selected_questions]
        print(f"Selected question IDs: {question_ids}")
        
        # Create exam
        exam = Exam.create(
            subject_id=request.subject_id,
            code=exam_code,
            title=exam_title,
            duration_minutes=request.duration_minutes,
            num_questions=request.num_questions,
            generated_by=request.generated_by,
            question_ids=question_ids
        )
        
        print(f"Exam created: {exam}")
        
        if exam:
            exam_dict = exam.to_dict()
            print(f"Exam dict: {exam_dict}")
            return ExamResponse(**exam_dict)
        else:
            raise HTTPException(status_code=400, detail="Failed to create exam")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating exam: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{exam_id}/versions")
async def add_exam_version(exam_id: int, question_ids: List[int]):
    """Thêm version mới cho exam"""
    try:
        exam = Exam.get_by_id(exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        
        version = exam.add_version(question_ids)
        if version:
            return {"success": True, "version": version.to_dict()}
        else:
            raise HTTPException(status_code=400, detail="Failed to add version")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/versions/{version_id}")
async def get_exam_version(version_id: int):
    """Lấy exam version theo ID"""
    try:
        version = ExamVersion.get_by_id(version_id)
        if version:
            return {"success": True, "version": version.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Exam version not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 