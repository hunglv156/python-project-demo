from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..models.subject import Subject

router = APIRouter(prefix="/subjects", tags=["Subjects"])

class SubjectResponse(BaseModel):
    id: int
    name: str
    created_at: str

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects():
    """Lấy tất cả subjects"""
    try:
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