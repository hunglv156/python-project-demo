from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List
from ..models.subject import Subject
from ..models.user import User
from ..middleware.auth import require_auth, optional_auth, get_user_subjects_filter

router = APIRouter(prefix="/subjects", tags=["Subjects"])

class SubjectResponse(BaseModel):
    id: int
    name: str
    created_at: str

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    request: Request,
    current_user: User = Depends(optional_auth)
):
    """Lấy tất cả subjects"""
    try:
        # Nếu không có user đăng nhập, trả về tất cả môn học
        if not current_user:
            subjects = Subject.get_all()
            return [SubjectResponse(**subject.to_dict()) for subject in subjects]
        
        # Lấy filter môn học cho user hiện tại
        allowed_subjects = get_user_subjects_filter(request)
        
        if allowed_subjects:
            # Editor chỉ thấy môn học được phân công
            subjects = []
            for subject_id in allowed_subjects:
                subject = Subject.get_by_id(subject_id)
                if subject:
                    subjects.append(subject)
            return [SubjectResponse(**subject.to_dict()) for subject in subjects]
        else:
            # Admin thấy tất cả môn học
            subjects = Subject.get_all()
            return [SubjectResponse(**subject.to_dict()) for subject in subjects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: int):
    """Lấy subject theo ID"""
    try:
        subject = Subject.get_by_id(subject_id)
        if subject:
            return SubjectResponse(**subject.to_dict())
        else:
            raise HTTPException(status_code=404, detail="Subject not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=SubjectResponse)
async def create_subject(name: str):
    """Tạo subject mới"""
    try:
        subject = Subject.create(name)
        if subject:
            return SubjectResponse(**subject.to_dict())
        else:
            raise HTTPException(status_code=400, detail="Failed to create subject")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 