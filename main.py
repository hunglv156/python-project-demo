import tkinter as tk
from tkinter import messagebox
import threading
import uvicorn
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.main import app as fastapi_app
from frontend.views import LoginView, DashboardView
from frontend.api_client import APIClient
from frontend.config import config

class TestManagementApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.BACKGROUND_COLOR)
        
        # Store reference to app in root
        self.root.app = self
        
        # Center window
        self.center_window()
        
        # Current view
        self.current_view = None
        self.user_data = None
        self.api_client = APIClient()
        
        # Start backend server
        self.start_backend()
        
        # Show login view
        self.show_login()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def start_backend(self):
        """Start FastAPI backend server in background thread"""
        def run_server():
            uvicorn.run(
                fastapi_app,
                host="127.0.0.1",
                port=8000,
                log_level="error"
            )
        
        self.backend_thread = threading.Thread(target=run_server, daemon=True)
        self.backend_thread.start()
    
    def show_login(self):
        """Show login view"""
        self.clear_current_view()
        self.current_view = LoginView(self.root, self.on_login_success, self.api_client)
        self.current_view.pack(expand=True, fill='both')
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.clear_current_view()
        self.current_view = DashboardView(self.root, self.user_data, self.on_logout, self.api_client)
        self.current_view.pack(expand=True, fill='both')
    
    def show_view(self, view_class, *args):
        """Show a specific view"""
        self.clear_current_view()
        self.current_view = view_class(self.root, *args)
        self.current_view.pack(expand=True, fill='both')
    
    def clear_current_view(self):
        """Clear current view"""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.user_data = user_data
        self.show_dashboard()
    
    def on_logout(self):
        """Handle logout"""
        self.user_data = None
        self.show_login()
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            sys.exit()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        app = TestManagementApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 