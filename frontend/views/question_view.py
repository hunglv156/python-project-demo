import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any
from ..config import config
from ..api_client import APIClient

class QuestionView(tk.Frame):
    def __init__(self, parent, user_data: Dict[str, Any]):
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = APIClient()
        self.questions = []
        self.subjects = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup question view UI"""
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
            text="Question Management",
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
        
        # Action buttons (for editor role)
        if self.user_data.get('role') == 'editor':
            self.setup_action_buttons(content_frame)
        
        # Filter area
        self.setup_filter_area(content_frame)
        
        # Questions list
        self.setup_questions_list(content_frame)
    
    def setup_action_buttons(self, parent):
        """Setup action buttons for editor role"""
        button_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Add question button
        add_button = tk.Button(
            button_frame,
            text="Add New Question",
            font=config.NORMAL_FONT,
            bg=config.SUCCESS_COLOR,
            fg="black",
            command=self.add_question
        )
        add_button.pack(side='left', padx=(0, 10))
        
        # Delete question button
        delete_button = tk.Button(
            button_frame,
            text="Delete Question",
            font=config.NORMAL_FONT,
            bg=config.ERROR_COLOR,
            fg="black",
            command=self.delete_selected_question
        )
        delete_button.pack(side='left', padx=(0, 10))
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame,
            text="Refresh",
            font=config.NORMAL_FONT,
            bg=config.SECONDARY_COLOR,
            fg="black",
            command=self.load_questions
        )
        refresh_button.pack(side='right')
    
    def setup_filter_area(self, parent):
        """Setup filter area"""
        filter_frame = tk.LabelFrame(parent, text="Filter", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        filter_frame.pack(fill='x', pady=(0, 20))
        
        # Subject filter
        subject_label = tk.Label(
            filter_frame,
            text="Subject:",
            font=config.NORMAL_FONT,
            bg=config.BACKGROUND_COLOR
        )
        subject_label.pack(side='left', padx=10, pady=10)
        
        self.subject_var = tk.StringVar()
        self.subject_combobox = ttk.Combobox(
            filter_frame,
            textvariable=self.subject_var,
            font=config.NORMAL_FONT,
            state="readonly"
        )
        self.subject_combobox.pack(side='left', padx=(0, 20), pady=10)
        self.subject_combobox.bind('<<ComboboxSelected>>', self.on_subject_changed)
    
    def setup_questions_list(self, parent):
        """Setup questions list"""
        list_frame = tk.LabelFrame(parent, text="Questions", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        list_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Subject', 'Question', 'Unit', 'Mark', 'Choices')
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
        self.tree.bind('<Double-1>', self.on_question_double_click)
    
    def load_data(self):
        """Load subjects and questions"""
        try:
            # Load subjects
            self.subjects = self.api_client.get_subjects()
            subject_names = ['All'] + [subject['name'] for subject in self.subjects]
            self.subject_combobox['values'] = subject_names
            self.subject_combobox.set('All')
            
            # Load questions
            self.load_questions()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            # Return to dashboard on error
            self.go_back()
    
    def load_questions(self):
        """Load questions based on filter"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get selected subject
            subject_name = self.subject_var.get()
            subject_id = None
            if subject_name != 'All':
                for subject in self.subjects:
                    if subject['name'] == subject_name:
                        subject_id = int(subject['id'])
                        break
            
            # Load questions
            self.questions = self.api_client.get_questions(subject_id)
            
            # Add to treeview
            for question in self.questions:
                try:
                    subject_name = "Unknown"
                    for subject in self.subjects:
                        if int(subject['id']) == int(question['subject_id']):
                            subject_name = subject['name']
                            break
                    
                    question_text = question.get('question', '')
                    if len(question_text) > 50:
                        question_text = question_text[:50] + "..."
                    
                    self.tree.insert('', 'end', values=(
                        question.get('id', ''),
                        subject_name,
                        question_text,
                        question.get('unit_text', ''),
                        question.get('mark', ''),
                        len(question.get('choices', []))
                    ))
                except Exception as e:
                    # Skip problematic questions
                    continue
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {str(e)}")
    
    def on_subject_changed(self, event):
        """Handle subject filter change"""
        self.load_questions()
    
    def on_question_double_click(self, event):
        """Handle question double click"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            question_id = item['values'][0]
            self.show_question_details(question_id)
    
    def get_selected_question_id(self):
        """Get selected question ID"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            return item['values'][0]
        return None
    
    def add_question(self):
        """Add new question"""
        self.show_question_dialog()
    
    def delete_selected_question(self):
        """Delete selected question"""
        question_id = self.get_selected_question_id()
        if question_id:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?"):
                try:
                    self.api_client.delete_question(question_id)
                    messagebox.showinfo("Success", "Question deleted successfully")
                    self.load_questions()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete question: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please select a question to delete")
    
    def show_question_details(self, question_id):
        """Show question details"""
        try:
            question = self.api_client.get_question(question_id)
            if question:
                self.show_question_dialog(question)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load question details: {str(e)}")
    
    def show_question_dialog(self, question=None, read_only=False):
        """Show question dialog for add/edit/view"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Question" if not question else f"Question {question['id']}")
        dialog.geometry("700x600")
        dialog.configure(bg=config.BACKGROUND_COLOR)
        
        # Make dialog modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Variables
        subject_var = tk.StringVar()
        unit_var = tk.StringVar()
        question_var = tk.StringVar()
        mark_var = tk.StringVar(value="1.0")
        mix_choices_var = tk.BooleanVar(value=True)
        image_var = tk.StringVar()
        
        # Subject selection
        subject_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        subject_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(subject_frame, text="Subject:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        subject_combobox = ttk.Combobox(subject_frame, textvariable=subject_var, values=[s['name'] for s in self.subjects], state="readonly")
        subject_combobox.pack(side='left', padx=(10, 0))
        
        # Unit
        unit_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        unit_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(unit_frame, text="Unit:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(unit_frame, textvariable=unit_var, font=config.NORMAL_FONT).pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Question text
        question_frame = tk.LabelFrame(dialog, text="Question Text", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        question_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        question_text = tk.Text(question_frame, font=config.NORMAL_FONT, wrap='word', height=6)
        question_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Image
        image_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        image_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(image_frame, text="Image:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(image_frame, textvariable=image_var, font=config.NORMAL_FONT).pack(side='left', padx=(10, 5), fill='x', expand=True)
        tk.Button(image_frame, text="Browse", command=lambda: self.browse_image(image_var)).pack(side='left')
        
        # Options
        options_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(options_frame, text="Mark:", font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        tk.Entry(options_frame, textvariable=mark_var, font=config.NORMAL_FONT, width=10).pack(side='left', padx=(10, 20))
        
        tk.Checkbutton(options_frame, text="Mix Choices", variable=mix_choices_var, font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR).pack(side='left')
        
        # Choices
        choices_frame = tk.LabelFrame(dialog, text="Choices", font=config.HEADER_FONT, bg=config.BACKGROUND_COLOR)
        choices_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        choices_container = tk.Frame(choices_frame, bg=config.BACKGROUND_COLOR)
        choices_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        choices = []
        correct_choice = tk.IntVar()
        
        def add_choice():
            choice_frame = tk.Frame(choices_container, bg=config.BACKGROUND_COLOR)
            choice_frame.pack(fill='x', pady=2)
            
            choice_var = tk.StringVar()
            choice_entry = tk.Entry(choice_frame, textvariable=choice_var, font=config.NORMAL_FONT)
            choice_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
            
            choice_radio = tk.Radiobutton(choice_frame, text="Correct", variable=correct_choice, value=len(choices), font=config.NORMAL_FONT, bg=config.BACKGROUND_COLOR)
            choice_radio.pack(side='left')
            
            def remove_choice():
                choice_frame.destroy()
                choices.remove((choice_var, choice_frame))
            
            remove_btn = tk.Button(choice_frame, text="Remove", command=remove_choice, font=config.NORMAL_FONT, bg=config.ERROR_COLOR, fg="black")
            remove_btn.pack(side='right')
            
            choices.append((choice_var, choice_frame))
        
        # Add choice button
        tk.Button(choices_container, text="Add Choice", command=add_choice, font=config.NORMAL_FONT, bg=config.PRIMARY_COLOR, fg="black").pack(pady=5)
        
        # Load existing data if editing
        if question:
            # Set subject
            for subject in self.subjects:
                if subject['id'] == question['subject_id']:
                    subject_var.set(subject['name'])
                    break
            
            unit_var.set(question.get('unit_text', ''))
            question_text.insert('1.0', question['question'])
            mark_var.set(str(question.get('mark', 1.0)))
            mix_choices_var.set(question.get('mix_choices', 1) == 1)
            image_var.set(question.get('image', ''))
            
            # Load choices
            for choice in question.get('choices', []):
                add_choice()
                if choices:
                    choices[-1][0].set(choice['content'])
                    if choice['is_correct']:
                        correct_choice.set(len(choices) - 1)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=config.BACKGROUND_COLOR)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        if not read_only:
            def save_question():
                if not self.user_data.get('role') == 'editor':
                    messagebox.showerror("Error", "You dont have permission to edit questions")
                    return;
                try:
                    # Validate
                    if not subject_var.get():
                        messagebox.showerror("Error", "Please select a subject")
                        return
                    
                    if not question_text.get('1.0', 'end-1c').strip():
                        messagebox.showerror("Error", "Please enter question text")
                        return
                    
                    if len(choices) < 2:
                        messagebox.showerror("Error", "Please add at least 2 choices")
                        return
                    
                    # Check if a correct answer is selected
                    if correct_choice.get() == -1:
                        messagebox.showerror("Error", "Please select a correct answer")
                        return
                    
                    # Check if all choices have content
                    empty_choices = []
                    for i, (choice_var, _) in enumerate(choices):
                        if not choice_var.get().strip():
                            empty_choices.append(i + 1)
                    
                    if empty_choices:
                        if len(empty_choices) == 1:
                            messagebox.showerror("Error", f"Choice {empty_choices[0]} cannot be empty")
                        else:
                            messagebox.showerror("Error", f"Choices {', '.join(map(str, empty_choices))} cannot be empty")
                        return
                    
                    # Get subject ID
                    subject_id = None
                    for subject in self.subjects:
                        if subject['name'] == subject_var.get():
                            subject_id = int(subject['id'])
                            break
                    
                    # Prepare choices data
                    choices_data = []
                    for i, (choice_var, _) in enumerate(choices):
                        content = choice_var.get().strip()
                        if content:  # Only include non-empty choices
                            choices_data.append({
                                'content': content,
                                'is_correct': i == correct_choice.get(),
                                'position': len(choices_data)  # Use sequential position
                            })
                    
                    question_data = {
                        'subject_id': subject_id,
                        'unit_text': unit_var.get().strip(),
                        'question': question_text.get('1.0', 'end-1c').strip(),
                        'mark': float(mark_var.get()),
                        'mix_choices': 1 if mix_choices_var.get() else 0,
                        'image': image_var.get().strip() or None,
                        'created_by': self.user_data['id'],
                        'choices': choices_data
                    }
                    
                    if question:  # Update
                        self.api_client.update_question(question['id'], question_data)
                        messagebox.showinfo("Success", "Question updated successfully")
                    else:  # Create
                        self.api_client.create_question(question_data)
                        messagebox.showinfo("Success", "Question created successfully")
                    
                    dialog.destroy()
                    self.load_questions()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save question: {str(e)}")
            
            tk.Button(button_frame, text="Save", command=save_question, font=config.NORMAL_FONT, bg=config.SUCCESS_COLOR, fg="black").pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="Close", command=dialog.destroy, font=config.NORMAL_FONT, bg=config.PRIMARY_COLOR, fg="black").pack(side='right')
        
        # Add initial choices if creating new
        if not question and not read_only:
            for _ in range(4):
                add_choice()
    
    def browse_image(self, image_var):
        """Browse for image file"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if filename:
            image_var.set(filename)
    
    def go_back(self):
        """Go back to dashboard"""
        from .dashboard_view import DashboardView
        # Get the main app instance
        app = self.winfo_toplevel().app
        app.show_view(DashboardView, self.user_data, app.on_logout) 