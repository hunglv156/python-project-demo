from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from ..models.user import User
from ..middleware.session import set_session_data, clear_session_data

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    message: str = ""

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """Đăng nhập user"""
    try:
        user = User.authenticate(request.username, request.password)
        if user:
            # Lưu thông tin user vào session
            set_session_data(req, "user_id", user.id)
            set_session_data(req, "username", user.username)
            set_session_data(req, "role", user.role)
            
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

@router.post("/logout")
async def logout(req: Request):
    """Đăng xuất user"""
    try:
        clear_session_data(req)
        return {"success": True, "message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 