from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..models.exam import Exam, ExamVersion

router = APIRouter(prefix="/exams", tags=["Exams"])

class CreateExamRequest(BaseModel):
    subject_id: int
    code: str
    title: str
    duration_minutes: int
    num_questions: int
    generated_by: int
    question_ids: List[int]

class ExamResponse(BaseModel):
    id: int
    subject_id: int
    code: str
    title: str
    duration_minutes: int
    num_questions: int
    generated_by: int
    created_at: str
    subject_name: str = None
    versions: List[dict]

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

@router.post("/", response_model=ExamResponse)
async def create_exam(request: CreateExamRequest):
    """Tạo exam mới"""
    try:
        exam = Exam.create(
            subject_id=request.subject_id,
            code=request.code,
            title=request.title,
            duration_minutes=request.duration_minutes,
            num_questions=request.num_questions,
            generated_by=request.generated_by,
            question_ids=request.question_ids
        )
        if exam:
            return ExamResponse(**exam.to_dict())
        else:
            raise HTTPException(status_code=400, detail="Failed to create exam")
    except Exception as e:
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