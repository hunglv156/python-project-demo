from typing import List, Dict, Any, Optional
import json
import random
from datetime import datetime
from ..database import db

class ExamVersionQuestion:
    def __init__(self, id: int, exam_version_id: int, question_id: int, choice_order_json: str):
        self.id = id
        self.exam_version_id = exam_version_id
        self.question_id = question_id
        self.choice_order_json = choice_order_json
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'exam_version_id': self.exam_version_id,
            'question_id': self.question_id,
            'choice_order_json': self.choice_order_json
        }

class ExamVersion:
    def __init__(self, id: int, exam_id: int, version_code: str, shuffle_seed: int, 
                 is_active: bool, created_at: str):
        self.id = id
        self.exam_id = exam_id
        self.version_code = version_code
        self.shuffle_seed = shuffle_seed
        self.is_active = is_active
        self.created_at = created_at
        self.questions = []
    
    @staticmethod
    def create(exam_id: int, version_code: str, questions: List[int]) -> 'ExamVersion':
        """Tạo exam version mới với shuffle choices"""
        try:
            shuffle_seed = random.randint(1, 1000000)
            
            # Insert exam version
            query = """
                INSERT INTO exam_versions (exam_id, version_code, shuffle_seed)
                VALUES (%s, %s, %s) RETURNING *
            """
            result = db.execute_single(query, (exam_id, version_code, shuffle_seed))
            
            if result:
                # Convert datetime to string if needed
                if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                    result['created_at'] = result['created_at'].isoformat()
                
                exam_version = ExamVersion(**result)
                
                # Insert questions với shuffled choices
                for question_id in questions:
                    # Lấy question và choices
                    from .question import Question, Choice
                    question = Question.get_by_id(question_id)
                    choices = Choice.get_by_question_id(question_id)
                    
                    if not question or not choices:
                        continue
                    
                    # Chỉ shuffle nếu mix_choice = true
                    if question.mix_choices:
                        # Shuffle choices với seed
                        random.seed(shuffle_seed + question_id)
                        shuffled_choices = choices.copy()
                        random.shuffle(shuffled_choices)
                        
                        # Lưu thứ tự mới
                        choice_order = [choice.id for choice in shuffled_choices]
                        choice_order_json = json.dumps(choice_order)
                    else:
                        # Giữ nguyên thứ tự gốc
                        choice_order = [choice.id for choice in choices]
                        choice_order_json = json.dumps(choice_order)
                    
                    # Insert vào exam_version_questions
                    evq_query = """
                        INSERT INTO exam_version_questions (exam_version_id, question_id, choice_order_json)
                        VALUES (%s, %s, %s) RETURNING *
                    """
                    evq_result = db.execute_single(evq_query, (exam_version.id, question_id, choice_order_json))
                    if evq_result:
                        exam_version.questions.append(ExamVersionQuestion(**evq_result))
                
                return exam_version
            return None
        except Exception as e:
            print(f"Error creating exam version: {e}")
            raise
    
    @staticmethod
    def get_by_id(version_id: int) -> Optional['ExamVersion']:
        """Lấy exam version theo ID"""
        query = "SELECT * FROM exam_versions WHERE id = %s"
        result = db.execute_single(query, (version_id,))
        if result:
            exam_version = ExamVersion(**result)
            # Lấy questions
            evq_query = "SELECT * FROM exam_version_questions WHERE exam_version_id = %s"
            evq_results = db.execute_query(evq_query, (version_id,))
            exam_version.questions = [ExamVersionQuestion(**evq_result) for evq_result in evq_results]
            return exam_version
        return None
    
    def get_questions_with_shuffled_choices(self) -> List[Dict[str, Any]]:
        """Lấy questions với choices đã được shuffle"""
        from .question import Question, Choice
        
        questions_data = []
        
        for evq in self.questions:
            # Lấy question
            question = Question.get_by_id(evq.question_id)
            if not question:
                continue
            
            # Lấy choices gốc
            original_choices = Choice.get_by_question_id(question.id)
            
            # Parse shuffled order
            try:
                shuffled_order = json.loads(evq.choice_order_json)
            except:
                shuffled_order = [choice.id for choice in original_choices]
            
            # Tạo choices theo thứ tự đã shuffle
            shuffled_choices = []
            for choice_id in shuffled_order:
                for choice in original_choices:
                    if choice.id == choice_id:
                        shuffled_choices.append(choice)
                        break
            
            # Tạo question data
            question_data = {
                'question_text': question.question,
                'unit': question.unit_text,
                'mark': float(question.mark),
                'image': question.image,
                'choices': []
            }
            
            # Thêm choices với thứ tự mới
            for i, choice in enumerate(shuffled_choices):
                question_data['choices'].append({
                    'letter': chr(ord('a') + i),  # a, b, c, d...
                    'content': choice.content,
                    'is_correct': choice.is_correct
                })
            
            questions_data.append(question_data)
        
        return questions_data
    
    def to_dict(self) -> Dict[str, Any]:
        # Convert datetime to string if it's a datetime object
        created_at = self.created_at
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        
        return {
            'id': self.id,
            'exam_id': self.exam_id,
            'version_code': self.version_code,
            'shuffle_seed': self.shuffle_seed,
            'is_active': self.is_active,
            'created_at': created_at,
            'questions': [q.to_dict() for q in self.questions]
        }

class Exam:
    def __init__(self, id: int, subject_id: int, code: str, title: str, 
                 duration_minutes: int, num_questions: int, generated_by: int, created_at: str, 
                 subject_name: str = None):
        self.id = id
        self.subject_id = subject_id
        self.code = code
        self.title = title
        self.duration_minutes = duration_minutes
        self.num_questions = num_questions
        self.generated_by = generated_by
        self.created_at = created_at
        self.subject_name = subject_name
        self.versions = []
    
    @staticmethod
    def create(subject_id: int, code: str, title: str, duration_minutes: int, 
               num_questions: int, generated_by: int, question_ids: List[int]) -> 'Exam':
        """Tạo exam mới"""
        try:
            # Insert exam
            query = """
                INSERT INTO exams (subject_id, code, title, duration_minutes, num_questions, generated_by)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
            """
            result = db.execute_single(query, (subject_id, code, title, duration_minutes, num_questions, generated_by))
            
            if result:
                # Convert datetime to string if needed
                if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                    result['created_at'] = result['created_at'].isoformat()
                
                exam = Exam(**result)
                
                # Tạo version đầu tiên
                version_code = "001"
                exam_version = ExamVersion.create(exam.id, version_code, question_ids)
                if exam_version:
                    exam.versions.append(exam_version)
                
                return exam
            return None
        except Exception as e:
            print(f"Error creating exam: {e}")
            raise
    
    @staticmethod
    def get_all() -> List['Exam']:
        """Lấy tất cả exams"""
        query = """
            SELECT e.*, s.name as subject_name 
            FROM exams e 
            JOIN subjects s ON e.subject_id = s.id 
            ORDER BY e.created_at DESC
        """
        results = db.execute_query(query)
        return [Exam(**result) for result in results]
    
    @staticmethod
    def get_by_id(exam_id: int) -> Optional['Exam']:
        """Lấy exam theo ID"""
        query = """
            SELECT e.*, s.name as subject_name 
            FROM exams e 
            JOIN subjects s ON e.subject_id = s.id 
            WHERE e.id = %s
        """
        result = db.execute_single(query, (exam_id,))
        if result:
            exam = Exam(**result)
            # Lấy versions
            versions_query = "SELECT * FROM exam_versions WHERE exam_id = %s ORDER BY version_code"
            versions_results = db.execute_query(versions_query, (exam_id,))
            exam.versions = [ExamVersion(**version_result) for version_result in versions_results]
            return exam
        return None
    
    def get_versions(self) -> List[ExamVersion]:
        """Lấy tất cả versions của exam"""
        query = "SELECT * FROM exam_versions WHERE exam_id = %s ORDER BY version_code"
        results = db.execute_query(query, (self.id,))
        versions = []
        for result in results:
            version = ExamVersion(**result)
            # Lấy questions cho version
            evq_query = "SELECT * FROM exam_version_questions WHERE exam_version_id = %s"
            evq_results = db.execute_query(evq_query, (version.id,))
            version.questions = [ExamVersionQuestion(**evq_result) for evq_result in evq_results]
            versions.append(version)
        return versions
    
    def add_version(self, question_ids: List[int]) -> Optional[ExamVersion]:
        """Thêm version mới cho exam"""
        # Tìm version code tiếp theo
        max_version_query = """
            SELECT MAX(CAST(version_code AS INTEGER)) as max_version 
            FROM exam_versions 
            WHERE exam_id = %s
        """
        result = db.execute_single(max_version_query, (self.id,))
        next_version = 1
        if result and result['max_version']:
            next_version = result['max_version'] + 1
        
        version_code = f"{next_version:03d}"
        return ExamVersion.create(self.id, version_code, question_ids)
    
    def to_dict(self) -> Dict[str, Any]:
        # Convert datetime to string if it's a datetime object
        created_at = self.created_at
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'code': self.code,
            'title': self.title,
            'duration_minutes': self.duration_minutes,
            'num_questions': self.num_questions,
            'generated_by': self.generated_by,
            'created_at': created_at,
            'subject_name': self.subject_name,
            'versions': [v.to_dict() for v in self.versions] if self.versions else []
        } 