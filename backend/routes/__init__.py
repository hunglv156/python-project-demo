from .auth import router as auth_router
from .subjects import router as subjects_router
from .questions import router as questions_router
from .exams import router as exams_router
from .import_docx import router as import_router
from .test_session import router as test_session_router

__all__ = [
    'auth_router',
    'subjects_router', 
    'questions_router',
    'exams_router',
    'import_router',
    'test_session_router'
] 