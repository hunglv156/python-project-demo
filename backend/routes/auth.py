from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..models.user import User
from ..models.user_subject import UserSubject

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    assigned_subjects: Optional[list] = None
    message: str = ""

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Đăng nhập user"""
    try:
        user = User.authenticate(request.username, request.password)
        if user:
            # Lấy môn học được phân công nếu là editor
            assigned_subjects = []
            if user.role == 'editor':
                subject_ids = UserSubject.get_user_subjects(user.id)
                from ..models.subject import Subject
                for subject_id in subject_ids:
                    subject = Subject.get_by_id(subject_id)
                    if subject:
                        assigned_subjects.append(subject.to_dict())
            
            return LoginResponse(
                success=True,
                user=user.to_dict(),
                assigned_subjects=assigned_subjects,
                message="Login successful"
            )
        else:
            return LoginResponse(
                success=False,
                message="Invalid username or password"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user(user_id: int):
    """Lấy thông tin user theo ID"""
    try:
        user = User.get_by_id(user_id)
        if user:
            return {"success": True, "user": user.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout():
    """Đăng xuất user"""
    try:
        return {"success": True, "message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 