import os

class FrontendConfig:
    # API settings
    API_BASE_URL = "http://localhost:8000"
    
    # UI settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_TITLE = "Test Management System"
    
    # Colors
    PRIMARY_COLOR = "#2E86AB"
    SECONDARY_COLOR = "#A23B72"
    SUCCESS_COLOR = "#28A745"
    WARNING_COLOR = "#FFC107"
    ERROR_COLOR = "#DC3545"
    BACKGROUND_COLOR = "#F8F9FA"
    
    # Fonts
    TITLE_FONT = ("Arial", 16, "bold")
    HEADER_FONT = ("Arial", 12, "bold")
    NORMAL_FONT = ("Arial", 10)
    SMALL_FONT = ("Arial", 8)
    
    # File paths
    IMAGES_DIR = "images"
    UPLOADS_DIR = "uploads"

config = FrontendConfig() 