from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import json
import base64

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Khởi tạo session từ cookies
        if not hasattr(request.state, 'session'):
            request.state.session = {}
        
        # Đọc session từ cookies
        session_cookie = request.cookies.get('session')
        if session_cookie:
            try:
                session_data = json.loads(base64.b64decode(session_cookie).decode('utf-8'))
                request.state.session = session_data
            except:
                request.state.session = {}
        
        # Xử lý request
        response = await call_next(request)
        
        # Lưu session vào cookies
        if hasattr(request.state, 'session') and request.state.session:
            session_json = json.dumps(request.state.session)
            session_encoded = base64.b64encode(session_json.encode('utf-8')).decode('utf-8')
            response.set_cookie(
                key='session',
                value=session_encoded,
                max_age=3600,  # 1 giờ
                httponly=True,
                samesite='lax'
            )
        else:
            # Xóa cookie nếu session trống
            response.delete_cookie('session')
        
        return response

def get_session_data(request: Request) -> dict:
    """Lấy dữ liệu session từ request"""
    if not hasattr(request.state, 'session'):
        request.state.session = {}
    return request.state.session

def set_session_data(request: Request, key: str, value: any):
    """Lưu dữ liệu vào session"""
    if not hasattr(request.state, 'session'):
        request.state.session = {}
    request.state.session[key] = value

def clear_session_data(request: Request):
    """Xóa dữ liệu session"""
    if hasattr(request.state, 'session'):
        request.state.session.clear() 