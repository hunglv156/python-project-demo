import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from ..config import config
from ..api_client import APIClient

class ExamView(tk.Frame):
    def __init__(self, parent, user_data: Dict[str, Any], api_client: APIClient = None):
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = api_client or APIClient()
        self.exams = []
        self.subjects = []
        self.questions = []
        
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
            text="Exam Management",
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
        
        # Action buttons (for generator role)
        if self.user_data.get('role') == 'generator':
            self.setup_action_buttons(content_frame)
        
        # Exams list
        self.setup_exams_list(content_frame)
    
    def setup_action_buttons(self, parent):
        """Setup action buttons for generator role"""
        button_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Create exam button
        create_button = tk.Button(
            button_frame,
            text="Create New Exam",
            font=config.NORMAL_FONT,
            bg=config.SUCCESS_COLOR,
            fg="black",
            command=self.create_exam
        )
        create_button.pack(side='left', padx=(0, 10))
        
        # Add version button
        add_version_button = tk.Button(
            button_frame,
            text="Add Version to Exam",
            font=config.NORMAL_FONT,
            bg=config.PRIMARY_COLOR,
            fg="black",
            command=self.add_exam_version
        )
        add_version_button.pack(side='left', padx=(0, 10))
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame,
            text="Refresh",
            font=config.NORMAL_FONT,
            bg=config.SECONDARY_COLOR,
            fg="black",
            command=self.load_exams
        )
        refresh_button.pack(side='right')
    
    def setup_exams_list(self, parent):
        """Setup exams list"""
        list_frame = tk.LabelFrame(parent, text="Exams", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Code', 'Title', 'Subject', 'Duration', 'Questions', 'Versions')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Bind double click
        self.tree.bind('<Double-1>', self.on_exam_double_click)
    
    def load_data(self):
        """Load subjects, questions and exams"""
        try:
            # Load subjects
            self.subjects = self.api_client.get_subjects()
            
            # Load questions
            self.questions = self.api_client.get_questions()
            
            # Load exams
            self.load_exams()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
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
                
                self.tree.insert('', 'end', values=(
                    exam['id'],
                    exam['code'],
                    exam['title'],
                    subject_name,
                    f"{exam['duration_minutes']} min",
                    exam['num_questions'],
                    len(exam.get('versions', []))
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exams: {str(e)}")
    
    def get_selected_exam_id(self):
        """Get selected exam ID"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item['values'][0]
        return None
    
    def create_exam(self):
        """Create new exam"""
        self.show_exam_dialog()
    
    def add_exam_version(self):
        """Add version to selected exam"""
        exam_id = self.get_selected_exam_id()
        if exam_id:
            try:
                exam = self.api_client.get_exam(exam_id)
                if exam:
                    self.show_version_dialog(exam)
                else:
                    messagebox.showerror("Error", "Exam not found")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load exam: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please select an exam to add version")
    
    def on_exam_double_click(self, event):
        """Handle exam double click"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            exam_id = item['values'][0]
            self.show_exam_details(exam_id)
    
    def show_exam_details(self, exam_id):
        """Show exam details"""
        try:
            exam = self.api_client.get_exam(exam_id)
            if exam:
                self.show_exam_dialog(exam, read_only=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load exam details: {str(e)}")
    
    def show_exam_dialog(self, exam=None, read_only=False):
        """Show exam dialog for create/edit/view"""
        dialog = tk.Toplevel(self)
        dialog.title("Create New Exam" if not exam else f"Exam {exam['code']}")
        dialog.geometry("800x700")
        dialog.configure(bg=config.BACKGROUND_COLOR)
        
        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Variables
        subject_var = tk.StringVar()
        code_var = tk.StringVar()
        title_var = tk.StringVar()
        duration_var = tk.StringVar(value="60")
        num_questions_var = tk.StringVar(value="30")
        
        # Subject selection
        subject_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        subject_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(subject_frame, text="Subject:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        subject_combobox = ttk.Combobox(subject_frame, textvariable=subject_var, values=[s['name'] for s in self.subjects], state="readonly")
        subject_combobox.pack(side='left', padx=(10, 0))
        
        # Exam info
        info_frame = tk.LabelFrame(dialog, text="Exam Information", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        # Code
        code_frame = tk.Frame(info_frame, bg=config.BACKGROUND_COLOR)
        code_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(code_frame, text="Code:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(code_frame, textvariable=code_var, font=config.NORMAL_FONT).pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Title
        title_frame = tk.Frame(info_frame, bg=config.BACKGROUND_COLOR)
        title_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(title_frame, text="Title:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(title_frame, textvariable=title_var, font=config.NORMAL_FONT).pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Duration and Questions
        options_frame = tk.Frame(info_frame, bg=config.BACKGROUND_COLOR)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(options_frame, text="Duration (min):", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(options_frame, textvariable=duration_var, font=config.NORMAL_FONT, width=10).pack(side='left', padx=(10, 20))
        
        tk.Label(options_frame, text="Questions:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(options_frame, textvariable=num_questions_var, font=config.NORMAL_FONT, width=10).pack(side='left', padx=(10, 0))
        
        # Questions selection
        questions_frame = tk.LabelFrame(dialog, text="Select Questions", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        questions_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Filter by subject
        filter_frame = tk.Frame(questions_frame, bg=config.BACKGROUND_COLOR)
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter by Subject:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        filter_subject_var = tk.StringVar()
        filter_combobox = ttk.Combobox(filter_frame, textvariable=filter_subject_var, values=['All'] + [s['name'] for s in self.subjects], state="readonly")
        filter_combobox.pack(side='left', padx=(10, 0))
        filter_combobox.set('All')
        
        # Questions list
        questions_container = tk.Frame(questions_frame, bg=config.BACKGROUND_COLOR)
        questions_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Questions treeview
        question_columns = ('ID', 'Question', 'Unit', 'Mark', 'Selected')
        questions_tree = ttk.Treeview(questions_container, columns=question_columns, show='headings', height=10)
        
        for col in question_columns:
            questions_tree.heading(col, text=col)
            questions_tree.column(col, width=150)
        
        question_scrollbar = ttk.Scrollbar(questions_container, orient='vertical', command=questions_tree.yview)
        questions_tree.configure(yscrollcommand=question_scrollbar.set)
        
        questions_tree.pack(side='left', fill='both', expand=True)
        question_scrollbar.pack(side='right', fill='y')
        
        # Selected questions
        selected_questions = set()
        
        def load_filtered_questions():
            """Load questions based on filter"""
            # Clear existing items
            for item in questions_tree.get_children():
                questions_tree.delete(item)
            
            # Get filter subject
            filter_subject = filter_subject_var.get()
            filtered_questions = []
            
            if filter_subject == 'All':
                filtered_questions = self.questions
            else:
                subject_id = None
                for subject in self.subjects:
                    if subject['name'] == filter_subject:
                        subject_id = subject['id']
                        break
                
                if subject_id:
                    filtered_questions = [q for q in self.questions if q['subject_id'] == subject_id]
            
            # Add to treeview
            for question in filtered_questions:
                questions_tree.insert('', 'end', values=(
                    question['id'],
                    question['question'][:50] + "..." if len(question['question']) > 50 else question['question'],
                    question.get('unit_text', ''),
                    question.get('mark', ''),
                    "✓" if question['id'] in selected_questions else ""
                ))
        
        def toggle_question_selection():
            """Toggle question selection"""
            selection = questions_tree.selection()
            if selection:
                item = questions_tree.item(selection[0])
                question_id = item['values'][0]
                
                if question_id in selected_questions:
                    selected_questions.remove(question_id)
                else:
                    selected_questions.add(question_id)
                
                # Update display
                for item in questions_tree.get_children():
                    values = list(questions_tree.item(item)['values'])
                    if values[0] == question_id:
                        values[4] = "✓" if question_id in selected_questions else ""
                        questions_tree.item(item, values=values)
                        break
        
        # Bind events
        filter_combobox.bind('<<ComboboxSelected>>', lambda e: load_filtered_questions())
        questions_tree.bind('<Double-1>', lambda e: toggle_question_selection())
        
        # Load initial questions
        load_filtered_questions()
        
        # Load existing data if editing
        if exam:
            # Set values
            for subject in self.subjects:
                if subject['id'] == exam['subject_id']:
                    subject_var.set(subject['name'])
                    break
            
            code_var.set(exam['code'])
            title_var.set(exam['title'])
            duration_var.set(str(exam['duration_minutes']))
            num_questions_var.set(str(exam['num_questions']))
            
            # Disable editing if read-only
            if read_only:
                subject_combobox.config(state='disabled')
                code_var.set(exam['code'])
                title_var.set(exam['title'])
                duration_var.set(str(exam['duration_minutes']))
                num_questions_var.set(str(exam['num_questions']))
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        if not read_only:
            def save_exam():
                try:
                    # Validate
                    if not subject_var.get():
                        messagebox.showerror("Error", "Please select a subject")
                        return
                    
                    if not code_var.get().strip():
                        messagebox.showerror("Error", "Please enter exam code")
                        return
                    
                    if not title_var.get().strip():
                        messagebox.showerror("Error", "Please enter exam title")
                        return
                    
                    if len(selected_questions) == 0:
                        messagebox.showerror("Error", "Please select at least one question")
                        return
                    
                    # Get subject ID
                    subject_id = None
                    for subject in self.subjects:
                        if subject['name'] == subject_var.get():
                            subject_id = subject['id']
                            break
                    
                    exam_data = {
                        'subject_id': subject_id,
                        'code': code_var.get().strip(),
                        'title': title_var.get().strip(),
                        'duration_minutes': int(duration_var.get()),
                        'num_questions': int(num_questions_var.get()),
                        'generated_by': self.user_data['id'],
                        'question_ids': list(selected_questions)
                    }
                    
                    if exam:  # Update (not implemented in backend)
                        messagebox.showinfo("Info", "Update functionality not implemented")
                    else:  # Create
                        self.api_client.create_exam(exam_data)
                        messagebox.showinfo("Success", "Exam created successfully")
                    
                    dialog.destroy()
                    self.load_exams()
                    
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            tk.Button(button_frame, text="Save", command=save_exam, font=config.NORMAL_FONT, bg=config.SUCCESS_COLOR, fg="black").pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="Close", command=dialog.destroy, font=config.NORMAL_FONT, bg=config.PRIMARY_COLOR, fg="black").pack(side='right')
    
    def show_version_dialog(self, exam):
        """Show dialog to add version to exam"""
        dialog = tk.Toplevel(self)
        dialog.title(f"Add Version to Exam {exam['code']}")
        dialog.geometry("600x500")
        dialog.configure(bg=config.BACKGROUND_COLOR)
        
        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Questions selection
        questions_frame = tk.LabelFrame(dialog, text="Select Questions for New Version", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        questions_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Questions list
        questions_container = tk.Frame(questions_frame, bg=config.BACKGROUND_COLOR)
        questions_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Questions treeview
        question_columns = ('ID', 'Question', 'Unit', 'Mark', 'Selected')
        questions_tree = ttk.Treeview(questions_container, columns=question_columns, show='headings', height=15)
        
        for col in question_columns:
            questions_tree.heading(col, text=col)
            questions_tree.column(col, width=120)
        
        question_scrollbar = ttk.Scrollbar(questions_container, orient='vertical', command=questions_tree.yview)
        questions_tree.configure(yscrollcommand=question_scrollbar.set)
        
        questions_tree.pack(side='left', fill='both', expand=True)
        question_scrollbar.pack(side='right', fill='y')
        
        # Selected questions
        selected_questions = set()
        
        # Load questions for the same subject
        subject_questions = [q for q in self.questions if q['subject_id'] == exam['subject_id']]
        
        # Add to treeview
        for question in subject_questions:
            questions_tree.insert('', 'end', values=(
                question['id'],
                question['question'][:40] + "..." if len(question['question']) > 40 else question['question'],
                question.get('unit_text', ''),
                question.get('mark', ''),
                ""
            ))
        
        def toggle_question_selection():
            """Toggle question selection"""
            selection = questions_tree.selection()
            if selection:
                item = questions_tree.item(selection[0])
                question_id = item['values'][0]
                
                if question_id in selected_questions:
                    selected_questions.remove(question_id)
                else:
                    selected_questions.add(question_id)
                
                # Update display
                for item in questions_tree.get_children():
                    values = list(questions_tree.item(item)['values'])
                    if values[0] == question_id:
                        values[4] = "✓" if question_id in selected_questions else ""
                        questions_tree.item(item, values=values)
                        break
        
        # Bind double click
        questions_tree.bind('<Double-1>', lambda e: toggle_question_selection())
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def add_version():
            try:
                if len(selected_questions) == 0:
                    messagebox.showerror("Error", "Please select at least one question")
                    return
                
                self.api_client.add_exam_version(exam['id'], list(selected_questions))
                messagebox.showinfo("Success", "Version added successfully")
                dialog.destroy()
                self.load_exams()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(button_frame, text="Add Version", command=add_version, font=config.NORMAL_FONT, bg=config.SUCCESS_COLOR, fg="black").pack(side='left', padx=(0, 10))
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, font=config.NORMAL_FONT, bg=config.PRIMARY_COLOR, fg="black").pack(side='right')
    
    def go_back(self):
        """Go back to dashboard"""
        from .dashboard_view import DashboardView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(DashboardView, self.user_data, app.on_logout, self.api_client) 