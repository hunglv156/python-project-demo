import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any
from ..config import config
from ..api_client import APIClient

class DashboardView(tk.Frame):
    def __init__(self, parent, user_data: Dict[str, Any], on_logout: Callable):
        super().__init__(parent)
        self.user_data = user_data
        self.on_logout = on_logout
        self.api_client = APIClient()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Main container
        main_frame = tk.Frame(self, bg=config.BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill='both')
        
        # Header
        header_frame = tk.Frame(main_frame, bg=config.PRIMARY_COLOR, height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=config.WINDOW_TITLE,
            font=config.TITLE_FONT,
            bg=config.PRIMARY_COLOR,
            fg="black"
        )
        title_label.pack(side='left', padx=20, pady=15)
        
        # User info
        user_info = f"Welcome, {self.user_data.get('username', 'User')} ({self.user_data.get('role', 'Unknown')})"
        user_label = tk.Label(
            header_frame,
            text=user_info,
            font=config.NORMAL_FONT,
            bg=config.PRIMARY_COLOR,
            fg="black"
        )
        user_label.pack(side='right', padx=20, pady=15)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=config.BACKGROUND_COLOR)
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Role-based menu
        self.setup_menu(content_frame)
    
    def setup_menu(self, parent):
        """Setup menu based on user role"""
        role = self.user_data.get('role', '')
        
        # Menu title
        menu_title = tk.Label(
            parent,
            text="Select an option:",
            font=config.HEADER_FONT,
            bg=config.BACKGROUND_COLOR
        )
        menu_title.pack(pady=(0, 20))
        
        # Menu buttons frame
        menu_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        menu_frame.pack()
        
        # Role-specific buttons
        if role == 'importer':
            self.create_menu_button(menu_frame, "Import DOCX", self.open_import_view)
        
        if role == 'editor':
            self.create_menu_button(menu_frame, "Manage Questions", self.open_question_view)
        
        if role == 'generator':
            self.create_menu_button(menu_frame, "Create Exam", self.open_exam_view)
        
        # Logout button
        logout_button = tk.Button(
            parent,
            text="Logout",
            font=config.NORMAL_FONT,
            bg=config.ERROR_COLOR,
            fg="black",
            command=self.logout,
            width=15,
            height=2
        )
        logout_button.pack(pady=(30, 0))
    
    def create_menu_button(self, parent, text, command):
        """Create a menu button"""
        button = tk.Button(
            parent,
            text=text,
            font=config.NORMAL_FONT,
            bg=config.SECONDARY_COLOR,
            fg="black",
            command=command,
            width=20,
            height=2
        )
        button.pack(pady=10)
    
    def open_import_view(self):
        """Open import view"""
        from .import_view import ImportView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(ImportView, self.user_data)
    
    def open_question_view(self):
        """Open question view"""
        from .question_view import QuestionView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(QuestionView, self.user_data)
    
    def open_exam_view(self):
        """Open exam view"""
        from .exam_view import ExamView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(ExamView, self.user_data)
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Get the main app instance
            app = self.winfo_toplevel().app
            app.on_logout() 