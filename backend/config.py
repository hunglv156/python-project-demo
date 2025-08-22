import os
from typing import Optional

class Settings:
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:python_project@localhost:5432/python_project"
    
    # Application settings
    APP_NAME: str = "Exam Management System"
    APP_VERSION: str = "1.0.0"
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    IMAGES_DIR: str = "images"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    
    @classmethod
    def get_database_url(cls) -> str:
        return os.getenv("DATABASE_URL", cls.DATABASE_URL)
    
    @classmethod
    def get_upload_dir(cls) -> str:
        return os.getenv("UPLOAD_DIR", cls.UPLOAD_DIR)
    
    @classmethod
    def get_images_dir(cls) -> str:
        return os.getenv("IMAGES_DIR", cls.IMAGES_DIR)

settings = Settings() 