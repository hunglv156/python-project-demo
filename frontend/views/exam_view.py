import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
import os
from PIL import Image, ImageTk
from ..config import config
from ..api_client import APIClient

class ExamView(tk.Frame):
    def __init__(self, parent, user_data: Dict[str, Any], api_client: APIClient = None):
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = api_client or APIClient()
        self.exams = []
        self.subjects = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup exam view UI"""
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
            text="Tạo Đề Thi",
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
        
        # Create exam section
        self.setup_create_exam_section(content_frame)
        
        # Exams list section
        self.setup_exams_list_section(content_frame)
    
    def setup_create_exam_section(self, parent):
        """Setup section tạo đề thi"""
        create_frame = tk.LabelFrame(parent, text="Tạo Đề Thi Mới", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        create_frame.pack(fill='x', pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(create_frame, bg=config.BACKGROUND_COLOR)
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # Subject selection
        subject_frame = tk.Frame(form_frame, bg=config.BACKGROUND_COLOR)
        subject_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            subject_frame,
            text="Môn thi:",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR
        ).pack(side='left')
        
        self.subject_var = tk.StringVar()
        self.subject_combobox = ttk.Combobox(
            subject_frame,
            textvariable=self.subject_var,
            font=config.NORMAL_FONT,
            state="readonly",
            width=30
        )
        self.subject_combobox.pack(side='left', padx=(10, 0))
        
        # Bind subject selection change
        self.subject_combobox.bind('<<ComboboxSelected>>', lambda e: self.update_subject_info())
        
        # Duration frame
        duration_frame = tk.Frame(form_frame, bg=config.BACKGROUND_COLOR)
        duration_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            duration_frame,
            text="Thời gian thi (phút):",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR
        ).pack(side='left')
        
        self.duration_var = tk.StringVar(value="60")
        duration_entry = tk.Entry(
            duration_frame,
            textvariable=self.duration_var,
            font=config.NORMAL_FONT,
            width=10
        )
        duration_entry.pack(side='left', padx=(10, 0))
        
        # Number of questions frame
        questions_frame = tk.Frame(form_frame, bg=config.BACKGROUND_COLOR)
        questions_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            questions_frame,
            text="Số câu hỏi:",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR
        ).pack(side='left')
        
        self.questions_var = tk.StringVar(value="10")
        questions_entry = tk.Entry(
            questions_frame,
            textvariable=self.questions_var,
            font=config.NORMAL_FONT,
            width=10
        )
        questions_entry.pack(side='left', padx=(10, 0))
        
        # Subject info label
        self.subject_info_label = tk.Label(
            questions_frame,
            text="",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR,
            fg="blue"
        )
        self.subject_info_label.pack(side='left', padx=(20, 0))
        
        # Create button
        create_button = tk.Button(
            form_frame,
            text="Tạo Đề Thi",
            font=config.NORMAL_FONT,
            bg=config.SUCCESS_COLOR,
            fg="black",
            command=self.create_exam,
            width=15
        )
        create_button.pack(pady=(10, 0))
    
    def setup_exams_list_section(self, parent):
        """Setup section danh sách đề thi"""
        list_frame = tk.LabelFrame(parent, text="Danh Sách Đề Thi", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Mã đề', 'Môn thi', 'Thời gian', 'Số câu', 'Ngày tạo')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        column_widths = {
            'ID': 50,
            'Mã đề': 100,
            'Môn thi': 150,
            'Thời gian': 100,
            'Số câu': 80,
            'Ngày tạo': 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Bind double click
        self.tree.bind('<Double-1>', self.on_exam_double_click)
    
    def load_data(self):
        """Load subjects and exams"""
        try:
            # Load subjects
            self.subjects = self.api_client.get_subjects()
            
            # Load exams
            self.load_exams()
            
            # Update subject combobox
            subject_names = [subject['name'] for subject in self.subjects]
            self.subject_combobox['values'] = subject_names
            if subject_names:
                self.subject_combobox.set(subject_names[0])
                self.update_subject_info()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def update_subject_info(self):
        """Update thông tin môn học được chọn"""
        selected_subject = self.subject_var.get()
        if selected_subject:
            # Tìm subject và số câu hỏi
            for subject in self.subjects:
                if subject['name'] == selected_subject:
                    try:
                        questions = self.api_client.get_questions(subject_id=subject['id'])
                        self.subject_info_label.config(
                            text=f"(Có {len(questions)} câu hỏi trong môn này)"
                        )
                    except:
                        self.subject_info_label.config(text="(Không thể load số câu hỏi)")
                    break
    
    def load_exams(self):
        """Load exams"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load exams
            self.exams = self.api_client.get_exams()
            
            # Add to treeview
            for exam in self.exams:
                subject_name = "Unknown"
                for subject in self.subjects:
                    if subject['id'] == exam['subject_id']:
                        subject_name = subject['name']
                        break
                
                # Format created_at
                created_at = exam.get('created_at', '')
                if created_at:
                    if isinstance(created_at, str):
                        created_at = created_at[:10]  # Lấy ngày tháng năm
                    else:
                        created_at = created_at.strftime('%Y-%m-%d')
                
                self.tree.insert('', 'end', values=(
                    exam['id'],
                    exam['code'],
                    subject_name,
                    f"{exam['duration_minutes']} phút",
                    exam['num_questions'],
                    created_at
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exams: {str(e)}")
    
    def create_exam(self):
        """Tạo đề thi mới"""
        # Validate input
        if not self.subject_var.get():
            messagebox.showerror("Error", "Vui lòng chọn môn thi")
            return
        
        try:
            duration = int(self.duration_var.get())
            if duration <= 0:
                messagebox.showerror("Error", "Thời gian thi phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Thời gian thi phải là số")
            return
        
        try:
            num_questions = int(self.questions_var.get())
            if num_questions <= 0:
                messagebox.showerror("Error", "Số câu hỏi phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Error", "Số câu hỏi phải là số")
            return
        
        # Get subject ID
        subject_id = None
        for subject in self.subjects:
            if subject['name'] == self.subject_var.get():
                subject_id = subject['id']
                break
        
        if not subject_id:
            messagebox.showerror("Error", "Môn học không hợp lệ")
            return
        
        # Check available questions
        try:
            questions = self.api_client.get_questions(subject_id=subject_id)
            if num_questions > len(questions):
                messagebox.showerror("Error", f"Số câu hỏi ({num_questions}) vượt quá số câu hỏi có sẵn ({len(questions)})")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Không thể kiểm tra số câu hỏi: {str(e)}")
            return
        
        # Create exam
        try:
            exam_data = {
                'subject_id': subject_id,
                'duration_minutes': duration,
                'num_questions': num_questions,
                'generated_by': self.user_data['id']
            }
            
            response = self.api_client.create_exam(exam_data)
            
            if response:
                messagebox.showinfo("Success", f"Tạo đề thi thành công!\nMã đề: {response.get('code', '')}")
                self.load_exams()  # Refresh list
            else:
                messagebox.showerror("Error", "Tạo đề thi thất bại")
                
        except Exception as e:
            messagebox.showerror("Error", f"Tạo đề thi thất bại: {str(e)}")
    
    def on_exam_double_click(self, event):
        """Handle exam double click - preview exam"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            exam_id = item['values'][0]
            self.preview_exam(exam_id)
    
    def preview_exam(self, exam_id):
        """Preview đề thi"""
        try:
            exam_data = self.api_client.get_exam_preview(exam_id)
            if exam_data:
                self.show_exam_preview_dialog(exam_data)
            else:
                messagebox.showerror("Error", "Không thể load đề thi")
        except Exception as e:
            messagebox.showerror("Error", f"Không thể preview đề thi: {str(e)}")
    
    def show_exam_preview_dialog(self, exam_data):
        """Hiển thị dialog preview đề thi"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Preview Đề Thi - {exam_data.get('code', '')}")
        dialog.geometry("1000x700")
        dialog.transient(self)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            header_frame,
            text=f"ĐỀ THI: {exam_data.get('code', '')}",
            font=('Arial', 16, 'bold')
        ).pack()
        
        tk.Label(
            header_frame,
            text=f"Môn: {exam_data.get('subject_name', '')}",
            font=('Arial', 12)
        ).pack()
        
        tk.Label(
            header_frame,
            text=f"Thời gian: {exam_data.get('duration_minutes', 0)} phút | Số câu: {exam_data.get('num_questions', 0)}",
            font=('Arial', 12)
        ).pack()
        
        # Create canvas with scrollbar for questions
        canvas_frame = tk.Frame(main_frame)
        canvas_frame.pack(fill='both', expand=True)
        
        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load questions content
        questions = exam_data.get('questions', [])
        
        for i, question in enumerate(questions, 1):
            # Question container
            question_container = tk.Frame(scrollable_frame, relief='groove', bd=2)
            question_container.pack(fill='x', pady=(0, 15), padx=5)
            
            # Question text
            question_text = question.get('question_text', '')
            question_label = tk.Label(
                question_container,
                text=f"Câu {i}: {question_text}",
                font=('Arial', 11, 'bold'),
                wraplength=800,
                justify='left',
                anchor='w'
            )
            question_label.pack(anchor='w', padx=10, pady=(10, 5))
            
            # Display image if exists
            image_path = question.get('image')
            if image_path:
                self.display_question_image(question_container, image_path)
            
            # Choices
            choices = question.get('choices', [])
            for j, choice in enumerate(choices):
                choice_letter = choice.get('letter', '').upper()
                choice_content = choice.get('content', '')
                is_correct = choice.get('is_correct', False)
                
                choice_text = f"  {choice_letter}. {choice_content}"
                if is_correct:
                    choice_text += " ✓"
                
                choice_label = tk.Label(
                    question_container,
                    text=choice_text,
                    font=('Arial', 10),
                    wraplength=750,
                    justify='left',
                    anchor='w',
                    fg='green' if is_correct else 'black'
                )
                choice_label.pack(anchor='w', padx=20, pady=2)
            
            # Add some space after each question
            tk.Frame(question_container, height=10).pack()
        
        # Close button
        close_button = tk.Button(
            main_frame,
            text="Đóng",
            font=('Arial', 12),
            command=dialog.destroy,
            width=10
        )
        close_button.pack(pady=(20, 0))
    
    def display_question_image(self, parent, image_path):
        """Hiển thị ảnh cho câu hỏi"""
        try:
            # Construct full path to image
            images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'images')
            full_image_path = os.path.join(images_dir, image_path)
            
            if os.path.exists(full_image_path):
                # Open and resize image
                original_image = Image.open(full_image_path)
                
                # Calculate new size (max width 400px, maintain aspect ratio)
                max_width = 400
                width, height = original_image.size
                if width > max_width:
                    ratio = max_width / width
                    new_width = max_width
                    new_height = int(height * ratio)
                    original_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(original_image)
                
                # Create image label
                image_label = tk.Label(parent, image=photo)
                image_label.image = photo  # Keep a reference to prevent garbage collection
                image_label.pack(pady=(5, 10), padx=10)
                
            else:
                # Show error if image not found
                error_label = tk.Label(
                    parent,
                    text=f"Không tìm thấy ảnh: {image_path}",
                    font=('Arial', 9),
                    fg='red'
                )
                error_label.pack(pady=(5, 10), padx=10)
                
        except Exception as e:
            # Show error if image loading fails
            error_label = tk.Label(
                parent,
                text=f"Lỗi load ảnh {image_path}: {str(e)}",
                font=('Arial', 9),
                fg='red'
            )
            error_label.pack(pady=(5, 10), padx=10)
    
    def go_back(self):
        """Go back to dashboard"""
        from .dashboard_view import DashboardView
        app = self.winfo_toplevel().app
        app.show_view(DashboardView, self.user_data, app.on_logout, self.api_client) 