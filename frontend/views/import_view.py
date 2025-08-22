import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any
import os
from ..config import config
from ..api_client import APIClient

class ImportView(tk.Frame):
    def __init__(self, parent, user_data: Dict[str, Any], api_client: APIClient = None):
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = api_client or APIClient()
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
            fg="black"
        )
        title_label.pack(side='left', padx=20, pady=15)
        
        # Back button
        back_button = tk.Button(
            header_frame,
            text="← Back",
            font=config.NORMAL_FONT,
            bg=config.SECONDARY_COLOR,
            fg="black",
            command=self.go_back
        )
        back_button.pack(side='right', padx=20, pady=15)
        
        # Content area
        content_frame = tk.Frame(main_frame, bg=config.BACKGROUND_COLOR)
        content_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # File selection
        self.setup_file_selection(content_frame)
        
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
            fg="black",
            command=self.browse_file
        )
        browse_button.pack(side='right', padx=10, pady=10)
    
    def setup_subject_selection(self, parent):
        """Setup subject selection area - DEPRECATED"""
        pass
    
    def setup_preview_area(self, parent):
        """Setup preview area with improved scrolling"""
        preview_frame = tk.LabelFrame(parent, text="Preview (Read-only)", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        preview_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Create a frame to hold text and scrollbar
        text_frame = tk.Frame(preview_frame, bg=config.BACKGROUND_COLOR)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Preview text (read-only) with improved scrolling
        self.preview_text = tk.Text(
            text_frame,
            font=config.NORMAL_FONT,
            wrap='word',
            height=20,  # Increased height for better viewing
            state='disabled',  # Make it read-only
        )
        
        # Vertical scrollbar
        preview_text_scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_text_scrollbar.set)
        
        # Horizontal scrollbar for long lines
        preview_text_h_scrollbar = ttk.Scrollbar(text_frame, orient='horizontal', command=self.preview_text.xview)
        self.preview_text.configure(xscrollcommand=preview_text_h_scrollbar.set)
        
        # Pack text and scrollbars
        self.preview_text.pack(side='left', fill='both', expand=True)
        preview_text_scrollbar.pack(side='right', fill='y')
        preview_text_h_scrollbar.pack(side='bottom', fill='x')
    
    def setup_action_buttons(self, parent):
        """Setup action buttons"""
        button_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x')
        
        # Import button
        self.import_button = tk.Button(
            button_frame,
            text="Import",
            font=config.NORMAL_FONT,
            bg=config.SUCCESS_COLOR,
            fg="black",
            command=self.import_file,
            width=15,
            state='disabled'  # Disabled by default
        )
        self.import_button.pack(side='left')
    
    def browse_file(self):
        """Browse for DOCX file"""
        file_path = filedialog.askopenfilename(
            title="Select DOCX file",
            filetypes=[("DOCX files", "*.docx"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(os.path.basename(file_path))
            # Auto preview when file is selected
            self.auto_preview_file()
    
    def load_subjects(self):
        """Load subjects from API - DEPRECATED"""
        pass
    
    def auto_preview_file(self):
        """Auto preview DOCX file when selected"""
        if not self.selected_file:
            return
        
        try:
            # Show loading
            try:
                self.update()
            except tk.TclError:
                # Widget might have been destroyed
                pass
            
            # Call API
            response = self.api_client.preview_docx(self.selected_file)
            
            # Display preview (kể cả khi có lỗi)
            self.display_preview(response)
            
            # Hiển thị thông báo nếu có lỗi nghiêm trọng
            if response.get('critical_errors'):
                messagebox.showerror(
                    "Critical Errors", 
                    "File has critical errors and cannot be imported.\n\n" + 
                    "\n".join(response['critical_errors'])
                )
                # Disable import button
                self.import_button.config(state='disabled')
            elif not response.get('success'):
                messagebox.showerror("Error", "Failed to preview file")
                self.import_button.config(state='disabled')
            else:
                # Enable import button if preview successful
                self.import_button.config(state='normal')
                
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed: {str(e)}")
            self.import_button.config(state='disabled')
           
    
    def preview_file(self):
        """Preview DOCX file - DEPRECATED"""
        pass
    
    def display_preview(self, response):
        """Display preview in text area with improved scrolling"""
        # Enable text widget temporarily to update content
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        
        # Display file metadata
        file_metadata = response.get('file_metadata', {})
        summary = "=== FILE INFORMATION ===\n"
        summary += f"Subject: {file_metadata.get('subject', 'N/A')}\n"
        summary += f"Lecturer: {file_metadata.get('lecturer', 'N/A')}\n"
        summary += "\n"
        
        # Display summary
        summary += "=== SUMMARY ===\n"
        summary += f"Total Questions: {response.get('total_questions', 0)}\n"
        summary += f"Valid: {response.get('valid', False)}\n\n"
        
        # Display critical errors (nếu có)
        if response.get('critical_errors'):
            summary += "=== CRITICAL ERRORS (Cannot Preview) ===\n"
            for error in response['critical_errors']:
                summary += f"❌ {error}\n"
            summary += "\n"
        
        # Display regular errors
        if response.get('errors'):
            summary += "=== ERRORS ===\n"
            for error in response['errors']:
                summary += f"⚠️ {error}\n"
            summary += "\n"
        
        # Display warnings
        if response.get('warnings'):
            summary += "=== WARNINGS ===\n"
            for warning in response['warnings']:
                summary += f"⚠️ {warning}\n"
            summary += "\n"
        
        # Display questions (chỉ nếu không có lỗi nghiêm trọng)
        if not response.get('critical_errors'):
            questions = response.get('questions', [])
            summary += "=== QUESTIONS ===\n"
            for i, question in enumerate(questions, 1):
                summary += f"Question {i}:\n"
                summary += f"Text: {question.get('question_text', 'N/A')}\n"
                summary += f"Unit: {question.get('unit', 'N/A')}\n"
                summary += f"Mark: {question.get('mark', 'N/A')}\n"
                summary += f"Mix Choices: {'Yes' if question.get('mix_choices') else 'No'}\n"
                summary += f"Answer: {question.get('answer', 'N/A').upper()}\n"
                summary += f"Image: {'Yes' if question.get('image') else 'No'}\n"
                
                # Hiển thị chi tiết các đáp án
                choices = question.get('choices', [])
                summary += f"Choices ({len(choices)}):\n"
                for choice in choices:
                    choice_letter = choice.get('letter', '').upper()
                    choice_content = choice.get('content', '')
                    is_correct = choice.get('is_correct', False)
                    correct_mark = " ✓" if is_correct else ""
                    summary += f"  {choice_letter}. {choice_content}{correct_mark}\n"
                
                summary += "\n"
        
        self.preview_text.insert(1.0, summary)
        
        # Scroll to top after inserting content
        self.preview_text.see("1.0")
        
        # Disable text widget again to make it read-only
        self.preview_text.config(state='disabled')
    
    def import_file(self):
        """Import DOCX file"""
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file first")
            return
        
        try:
            # Show loading
            try:
                self.update()
            except tk.TclError:
                # Widget might have been destroyed
                pass
            
            # Call API
            response = self.api_client.import_docx(
                self.selected_file,
                self.user_data['id']
            )
            
            if response.get('success'):
                imported_count = response.get('imported_questions', 0)
                total_count = response.get('total_questions', 0)
                skipped_count = response.get('skipped_questions', 0)
                
                message = f"Imported {imported_count} out of {total_count} questions"
                if skipped_count > 0:
                    message += f"\nSkipped {skipped_count} duplicate questions"
                
                messagebox.showinfo("Success", message)
                self.go_back()
            else:
                messagebox.showerror("Error", response.get('message', 'Import failed'))
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def go_back(self):
        """Go back to dashboard"""
        from .dashboard_view import DashboardView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(DashboardView, self.user_data, app.on_logout, self.api_client) 