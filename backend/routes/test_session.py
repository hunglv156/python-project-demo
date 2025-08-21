from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any
from ..models.user import User
from ..middleware.auth import optional_auth
from ..middleware.session import get_session_data

router = APIRouter(prefix="/test", tags=["Test Session"])

class SessionInfoResponse(BaseModel):
    session_data: Dict[str, Any]
    has_user: bool
    user_info: Dict[str, Any] = None

@router.get("/session", response_model=SessionInfoResponse)
async def get_session_info(request: Request):
    """Lấy thông tin session hiện tại"""
    try:
        session_data = get_session_data(request)
        has_user = "user_id" in session_data
        
        user_info = None
        if has_user:
            user = User.get_by_id(session_data.get("user_id"))
            if user:
                user_info = user.to_dict()
        
        return SessionInfoResponse(
            session_data=session_data,
            has_user=has_user,
            user_info=user_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-user")
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(optional_auth)
):
    """Lấy thông tin user hiện tại"""
    try:
        if current_user:
            return {
                "success": True,
                "user": current_user.to_dict(),
                "message": "User is logged in"
            }
        else:
            return {
                "success": False,
                "user": None,
                "message": "No user logged in"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 