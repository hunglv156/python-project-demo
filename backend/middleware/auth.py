from fastapi import HTTPException, Request
from typing import Optional
from ..models.user import User
from ..models.user_subject import UserSubject
from .session import get_session_data

def get_current_user(request: Request) -> Optional[User]:
    """Lấy thông tin user hiện tại từ session"""
    session_data = get_session_data(request)
    user_id = session_data.get("user_id")
    if user_id:
        return User.get_by_id(user_id)
    return None

def require_auth(request: Request) -> User:
    """Yêu cầu user phải đăng nhập"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

def optional_auth(request: Request) -> User:
    """Lấy user nếu đã đăng nhập, không bắt buộc"""
    return get_current_user(request)

def require_subject_access(request: Request, subject_id: int) -> User:
    """Yêu cầu user phải có quyền truy cập môn học"""
    user = require_auth(request)
    
    # Admin (importer, generator) có quyền truy cập tất cả môn học
    if user.role in ['importer', 'generator']:
        return user
    
    # Editor chỉ có quyền truy cập môn học được phân công
    if user.role == 'editor':
        if not UserSubject.user_has_subject_access(user.id, subject_id):
            raise HTTPException(
                status_code=403, 
                detail="Môn học này không thuộc bạn quản lý"
            )
        return user
    
    # Các role khác không có quyền
    raise HTTPException(status_code=403, detail="Insufficient permissions")

def get_user_subjects_filter(request: Request) -> list:
    """Lấy filter môn học cho user hiện tại"""
    user = get_current_user(request)
    if not user:
        return []
    
    # Admin có thể xem tất cả môn học
    if user.role in ['importer', 'generator']:
        return []
    
    # Editor chỉ xem được môn học được phân công
    if user.role == 'editor':
        return UserSubject.get_user_subjects(user.id)
    
    return [] 