import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any
import os
from ..config import config
from ..api_client import APIClient

class ImportView(tk.Frame):
    def __init__(self, parent, user_data: Dict[str, Any]):
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = APIClient()
        self.selected_file = None
        self.subjects = []
        
        self.setup_ui()
        self.load_subjects()
    
    def setup_ui(self):
        """Setup import UI"""
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
            text="Import DOCX",
            font=config.TITLE_FONT,
            bg=config.PRIMARY_COLOR,
            fg="white"
        )
        title_label.pack(side='left', padx=20, pady=15)
        
        # Back button
        back_button = tk.Button(
            header_frame,
            text="← Back",
            font=config.NORMAL_FONT,
            bg=config.SECONDARY_COLOR,
            fg="white",
            command=self.go_back
        )
        back_button.pack(side='right', padx=20, pady=15)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=config.BACKGROUND_COLOR)
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # File selection
        self.setup_file_selection(content_frame)
        
        # Subject selection
        self.setup_subject_selection(content_frame)
        
        # Preview area
        self.setup_preview_area(content_frame)
        
        # Action buttons
        self.setup_action_buttons(content_frame)
    
    def setup_file_selection(self, parent):
        """Setup file selection area"""
        file_frame = tk.LabelFrame(parent, text="File Selection", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        file_frame.pack(fill='x', pady=(0, 20))
        
        # File path display
        self.file_path_var = tk.StringVar()
        file_path_label = tk.Label(
            file_frame,
            textvariable=self.file_path_var,
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR,
            fg="gray"
        )
        file_path_label.pack(side='left', padx=10, pady=10, fill='x', expand=True)
        
        # Browse button
        browse_button = tk.Button(
            file_frame,
            text="Browse",
            font=config.NORMAL_FONT,
            bg=config.PRIMARY_COLOR,
            fg="white",
            command=self.browse_file
        )
        browse_button.pack(side='right', padx=10, pady=10)
    
    def setup_subject_selection(self, parent):
        """Setup subject selection area"""
        subject_frame = tk.LabelFrame(parent, text="Subject Selection", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        subject_frame.pack(fill='x', pady=(0, 20))
        
        # Subject combobox
        self.subject_var = tk.StringVar()
        self.subject_combobox = ttk.Combobox(
            subject_frame,
            textvariable=self.subject_var,
            font=config.NORMAL_FONT,
            state="readonly"
        )
        self.subject_combobox.pack(padx=10, pady=10, fill='x')
    
    def setup_preview_area(self, parent):
        """Setup preview area"""
        preview_frame = tk.LabelFrame(parent, text="Preview", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        preview_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Preview text
        self.preview_text = tk.Text(
            preview_frame,
            font=config.NORMAL_FONT,
            wrap='word',
            height=15
        )
        preview_text_scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_text_scrollbar.set)
        
        self.preview_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        preview_text_scrollbar.pack(side='right', fill='y', pady=10)
    
    def setup_action_buttons(self, parent):
        """Setup action buttons"""
        button_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x')
        
        # Preview button
        preview_button = tk.Button(
            button_frame,
            text="Preview",
            font=config.NORMAL_FONT,
            bg=config.WARNING_COLOR,
            fg="white",
            command=self.preview_file,
            width=15
        )
        preview_button.pack(side='left', padx=(0, 10))
        
        # Import button
        import_button = tk.Button(
            button_frame,
            text="Import",
            font=config.NORMAL_FONT,
            bg=config.SUCCESS_COLOR,
            fg="white",
            command=self.import_file,
            width=15
        )
        import_button.pack(side='left')
    
    def browse_file(self):
        """Browse for DOCX file"""
        file_path = filedialog.askopenfilename(
            title="Select DOCX file",
            filetypes=[("DOCX files", "*.docx"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(os.path.basename(file_path))
    
    def load_subjects(self):
        """Load subjects from API"""
        try:
            self.subjects = self.api_client.get_subjects()
            subject_names = [subject['name'] for subject in self.subjects]
            self.subject_combobox['values'] = subject_names
            if subject_names:
                self.subject_combobox.set(subject_names[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subjects: {str(e)}")
    
    def preview_file(self):
        """Preview DOCX file"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            # Show loading
            self.config(cursor="wait")
            self.update()
            
            # Call API
            response = self.api_client.preview_docx(self.selected_file)
            
            if response.get('success'):
                # Display preview
                self.display_preview(response)
            else:
                messagebox.showerror("Error", "Failed to preview file")
                
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed: {str(e)}")
        finally:
            self.config(cursor="")
    
    def display_preview(self, response):
        """Display preview in text area"""
        self.preview_text.delete(1.0, tk.END)
        
        # Display summary
        summary = f"Total Questions: {response.get('total_questions', 0)}\n"
        summary += f"Valid: {response.get('valid', False)}\n\n"
        
        if response.get('errors'):
            summary += "Errors:\n"
            for error in response['errors']:
                summary += f"- {error}\n"
            summary += "\n"
        
        if response.get('warnings'):
            summary += "Warnings:\n"
            for warning in response['warnings']:
                summary += f"- {warning}\n"
            summary += "\n"
        
        # Display questions
        questions = response.get('questions', [])
        for i, question in enumerate(questions, 1):
            summary += f"Question {i}:\n"
            summary += f"Text: {question.get('question_text', 'N/A')}\n"
            summary += f"Unit: {question.get('unit', 'N/A')}\n"
            summary += f"Mark: {question.get('mark', 'N/A')}\n"
            summary += f"Answer: {question.get('answer', 'N/A')}\n"
            summary += f"Choices: {len(question.get('choices', []))}\n"
            if question.get('image'):
                summary += f"Image: {question['image']}\n"
            summary += "\n"
        
        self.preview_text.insert(1.0, summary)
    
    def import_file(self):
        """Import DOCX file"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        if not self.subject_var.get():
            messagebox.showerror("Error", "Please select a subject")
            return
        
        # Get subject ID
        subject_name = self.subject_var.get()
        subject_id = None
        for subject in self.subjects:
            if subject['name'] == subject_name:
                subject_id = subject['id']
                break
        
        if not subject_id:
            messagebox.showerror("Error", "Invalid subject")
            return
        
        try:
            # Show loading
            self.config(cursor="wait")
            self.update()
            
            # Call API
            response = self.api_client.import_docx(
                self.selected_file,
                subject_id,
                self.user_data['id']
            )
            
            if response.get('success'):
                messagebox.showinfo(
                    "Success", 
                    f"Imported {response.get('imported_questions', 0)} out of {response.get('total_questions', 0)} questions"
                )
                self.go_back()
            else:
                messagebox.showerror("Error", response.get('message', 'Import failed'))
                
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {str(e)}")
        finally:
            self.config(cursor="")
    
    def go_back(self):
        """Go back to dashboard"""
        from .dashboard_view import DashboardView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(DashboardView, self.user_data, app.on_logout) 