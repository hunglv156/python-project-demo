from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    message: str = ""

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Đăng nhập user"""
    try:
        user = User.authenticate(request.username, request.password)
        if user:
            return LoginResponse(
                success=True,
                user=user.to_dict(),
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