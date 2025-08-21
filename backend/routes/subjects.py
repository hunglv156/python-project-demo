from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from ..models.subject import Subject
from ..models.user_subject import UserSubject

router = APIRouter(prefix="/subjects", tags=["Subjects"])

class SubjectResponse(BaseModel):
    id: int
    name: str
    created_at: str

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(user_id: Optional[int] = Query(None)):
    """Lấy subjects theo user_id"""
    try:
        if user_id:
            # Lấy môn học được phân công cho user
            subject_ids = UserSubject.get_user_subjects(user_id)
            
            # Nếu user không có môn học được phân công (như importer), trả về tất cả
            if not subject_ids:
                subjects = Subject.get_all()
                return [SubjectResponse(**subject.to_dict()) for subject in subjects]
            
            # Nếu có môn học được phân công, trả về các môn đó
            subjects = []
            for subject_id in subject_ids:
                subject = Subject.get_by_id(subject_id)
                if subject:
                    subjects.append(subject)
            return [SubjectResponse(**subject.to_dict()) for subject in subjects]
        else:
            # Không có user_id thì trả về tất cả
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