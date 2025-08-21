import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from ..config import config
from ..api_client import APIClient

class LoginView(tk.Frame):
    def __init__(self, parent, on_login_success: Callable, api_client: APIClient):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.api_client = api_client
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup login UI"""
        # Main container
        main_frame = tk.Frame(self, bg=config.BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill='both')
        
        # Center the login form
        center_frame = tk.Frame(main_frame, bg=config.BACKGROUND_COLOR)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = tk.Label(
            center_frame,
            text=config.WINDOW_TITLE,
            font=config.TITLE_FONT,
            bg=config.BACKGROUND_COLOR,
            fg=config.PRIMARY_COLOR
        )
        title_label.pack(pady=(0, 30))
        
        # Login form
        form_frame = tk.Frame(center_frame, bg=config.BACKGROUND_COLOR)
        form_frame.pack()
        
        # Username
        username_label = tk.Label(
            form_frame,
            text="Username:",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR
        )
        username_label.pack(anchor='w', pady=(0, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=config.NORMAL_FONT,
            width=30
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR
        )
        password_label.pack(anchor='w', pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=config.NORMAL_FONT,
            width=30,
            show="*"
        )
        self.password_entry.pack(pady=(0, 25))
        
        # Login button
        login_button = tk.Button(
            form_frame,
            text="Login",
            font=config.NORMAL_FONT,
            bg=config.PRIMARY_COLOR,
            fg="black",
            command=self.login,
            width=15,
            height=2
        )
        login_button.pack()
        
        # Bind Enter key to login
        self.bind('<Return>', lambda e: self.login())
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            # Show loading
            self.config(cursor="wait")
            self.update()
            
            # Call API
            response = self.api_client.login(username, password)
            
            if response.get('success'):
                user_data = response.get('user', {})
                messagebox.showinfo("Success", f"Welcome, {user_data.get('username', 'User')}!")
                self.on_login_success(user_data)
            else:
                messagebox.showerror("Error", response.get('message', 'Login failed'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
        finally:
            try:
                self.config(cursor="")
            except tk.TclError:
                # Widget might have been destroyed
                pass 