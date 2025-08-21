from typing import List, Dict, Any, Optional
import logging
from ..database import db

logger = logging.getLogger(__name__)

class Choice:
    def __init__(self, id: int, question_id: int, content: str, is_correct: bool, position: int, created_at: str):
        self.id = id
        self.question_id = question_id
        self.content = content
        self.is_correct = is_correct
        self.position = position
        self.created_at = created_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'question_id': self.question_id,
            'content': self.content,
            'is_correct': self.is_correct,
            'position': self.position,
            'created_at': self.created_at
        }

class Question:
    def __init__(self, id: int, subject_id: int, unit_text: str, question: str, 
                 mix_choices: int, image: str, mark: float, created_by: int, 
                 created_at: str, updated_by: int = None, updated_at: str = None):
        self.id = id
        self.subject_id = subject_id
        self.unit_text = unit_text
        self.question = question
        self.mix_choices = mix_choices
        self.image = image
        self.mark = mark
        self.created_by = created_by
        self.created_at = created_at
        self.updated_by = updated_by
        # Convert updated_at to string if it's a datetime object
        if updated_at and hasattr(updated_at, 'isoformat'):
            self.updated_at = updated_at.isoformat()
        else:
            self.updated_at = updated_at
        self.choices = []
    
    @staticmethod
    def get_all(subject_id: Optional[int] = None) -> List['Question']:
        """Lấy tất cả questions, có thể filter theo subject"""
        try:
            if subject_id:
                query = """
                    SELECT * FROM questions 
                    WHERE subject_id = %s 
                    ORDER BY created_at DESC
                """
                results = db.execute_query(query, (subject_id,))
            else:
                query = "SELECT * FROM questions ORDER BY created_at DESC"
                results = db.execute_query(query)
            
            questions = []
            for result in results:
                try:
                    # Convert datetime to string if needed
                    if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                        result['created_at'] = result['created_at'].isoformat()
                    if 'updated_at' in result and result['updated_at'] and hasattr(result['updated_at'], 'isoformat'):
                        result['updated_at'] = result['updated_at'].isoformat()
                    
                    question = Question(**result)
                    question.choices = Choice.get_by_question_id(question.id)
                    questions.append(question)
                except Exception as e:
                    logger.error(f"Error processing question {result.get('id', 'unknown')}: {e}")
                    continue
            
            return questions
        except Exception as e:
            logger.error(f"Error in get_all: {e}")
            return []
    
    @staticmethod
    def get_by_id(question_id: int) -> Optional['Question']:
        """Lấy question theo ID"""
        try:
            query = "SELECT * FROM questions WHERE id = %s"
            result = db.execute_single(query, (question_id,))
            if result:
                # Convert datetime to string if needed
                if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                    result['created_at'] = result['created_at'].isoformat()
                if 'updated_at' in result and result['updated_at'] and hasattr(result['updated_at'], 'isoformat'):
                    result['updated_at'] = result['updated_at'].isoformat()
                
                question = Question(**result)
                question.choices = Choice.get_by_question_id(question.id)
                return question
            return None
        except Exception as e:
            logger.error(f"Error in get_by_id for question {question_id}: {e}")
            return None
    
    @staticmethod
    def create(subject_id: int, unit_text: str, question: str, mix_choices: int,
               image: str, mark: float, created_by: int, choices: List[Dict[str, Any]]) -> 'Question':
        """Tạo question mới với choices"""
        try:
            logger.info(f"Creating question with subject_id={subject_id}, unit_text='{unit_text}', question='{question[:50]}...'")
            
            # Validate choices
            if not choices or len(choices) < 2:
                raise ValueError("Question must have at least 2 choices")
            
            # Check if there's at least one correct answer
            has_correct_answer = any(choice.get('is_correct', False) for choice in choices)
            if not has_correct_answer:
                raise ValueError("Question must have at least one correct answer")
            
            # Check if all choices have content
            empty_choices = []
            for i, choice in enumerate(choices):
                if not choice.get('content', '').strip():
                    empty_choices.append(i + 1)
            
            if empty_choices:
                if len(empty_choices) == 1:
                    raise ValueError(f"Choice {empty_choices[0]} cannot be empty")
                else:
                    raise ValueError(f"Choices {', '.join(map(str, empty_choices))} cannot be empty")
            
            # Insert question
            query = """
                INSERT INTO questions (subject_id, unit_text, question, mix_choices, image, mark, created_by, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NULL) RETURNING *
            """
            # Handle None image
            image_value = image if image else None
            result = db.execute_single(query, (subject_id, unit_text, question, mix_choices, image_value, mark, created_by))
            
            if result:
                logger.info(f"Question created with ID: {result.get('id')}")
                
                # Convert datetime to string if needed
                if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                    result['created_at'] = result['created_at'].isoformat()
                if 'updated_at' in result and result['updated_at'] and hasattr(result['updated_at'], 'isoformat'):
                    result['updated_at'] = result['updated_at'].isoformat()
                
                question_obj = Question(**result)
                
                # Insert choices
                for i, choice_data in enumerate(choices):
                    logger.info(f"Creating choice {i+1}: {choice_data}")
                    choice_query = """
                        INSERT INTO choices (question_id, content, is_correct, position)
                        VALUES (%s, %s, %s, %s) RETURNING *
                    """
                    choice_result = db.execute_single(choice_query, (
                        question_obj.id, 
                        choice_data['content'], 
                        choice_data['is_correct'], 
                        i + 1
                    ))
                    if choice_result:
                        # Convert datetime to string if needed
                        if 'created_at' in choice_result and hasattr(choice_result['created_at'], 'isoformat'):
                            choice_result['created_at'] = choice_result['created_at'].isoformat()
                        
                        question_obj.choices.append(Choice(**choice_result))
                        logger.info(f"Choice {i+1} created successfully")
                    else:
                        logger.error(f"Failed to create choice {i+1}")
                
                return question_obj
            else:
                logger.error("Failed to create question - no result returned")
                return None
                
        except Exception as e:
            logger.error(f"Error creating question: {str(e)}")
            raise
    
    def update(self, unit_text: str, question: str, mix_choices: int, image: str, 
               mark: float, updated_by: int, choices: List[Dict[str, Any]]) -> bool:
        """Cập nhật question"""
        try:
            # Validate choices
            if not choices or len(choices) < 2:
                raise ValueError("Question must have at least 2 choices")
            
            # Check if there's at least one correct answer
            has_correct_answer = any(choice.get('is_correct', False) for choice in choices)
            if not has_correct_answer:
                raise ValueError("Question must have at least one correct answer")
            
            # Check if all choices have content
            empty_choices = []
            for i, choice in enumerate(choices):
                if not choice.get('content', '').strip():
                    empty_choices.append(i + 1)
            
            if empty_choices:
                if len(empty_choices) == 1:
                    raise ValueError(f"Choice {empty_choices[0]} cannot be empty")
                else:
                    raise ValueError(f"Choices {', '.join(map(str, empty_choices))} cannot be empty")
            
            # Update question
            query = """
                UPDATE questions 
                SET unit_text = %s, question = %s, mix_choices = %s, image = %s, 
                    mark = %s, updated_by = %s, updated_at = NOW()
                WHERE id = %s
            """
            db.execute_query(query, (unit_text, question, mix_choices, image, mark, updated_by, self.id))
            
            # Delete old choices
            db.execute_query("DELETE FROM choices WHERE question_id = %s", (self.id,))
            
            # Insert new choices
            for i, choice_data in enumerate(choices):
                choice_query = """
                    INSERT INTO choices (question_id, content, is_correct, position)
                    VALUES (%s, %s, %s, %s)
                """
                db.execute_query(choice_query, (
                    self.id, 
                    choice_data['content'], 
                    choice_data['is_correct'], 
                    i + 1
                ))
            
            # Update local attributes
            self.unit_text = unit_text
            self.question = question
            self.mix_choices = mix_choices
            self.image = image
            self.mark = mark
            self.updated_by = updated_by
            # updated_at will be set when reloading
            
            # Reload choices
            self.choices = Choice.get_by_question_id(self.id)
            
            return True
        except Exception as e:
            logger.error(f"Error updating question {self.id}: {str(e)}")
            return False
    
    def delete(self) -> bool:
        """Xóa question và các choices liên quan"""
        try:
            # Tắt trigger tạm thời để tránh lỗi khi xóa choices
            db.execute_query("ALTER TABLE choices DISABLE TRIGGER ALL")
            
            try:
                # Xóa choices trước (foreign key constraint)
                db.execute_query("DELETE FROM choices WHERE question_id = %s", (self.id,))
                
                # Sau đó xóa question
                db.execute_query("DELETE FROM questions WHERE id = %s", (self.id,))
                
                return True
            finally:
                # Bật lại trigger
                db.execute_query("ALTER TABLE choices ENABLE TRIGGER ALL")
                
        except Exception as e:
            logger.error(f"Error deleting question {self.id}: {str(e)}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question thành dict"""
        # Convert datetime objects to strings
        created_at = self.created_at
        if hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        
        updated_at = self.updated_at
        if updated_at and hasattr(updated_at, 'isoformat'):
            updated_at = updated_at.isoformat()
        
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'unit_text': self.unit_text,
            'question': self.question,
            'mix_choices': self.mix_choices,
            'image': self.image,
            'mark': self.mark,
            'created_by': self.created_by,
            'created_at': created_at,
            'updated_by': self.updated_by,
            'updated_at': updated_at,
            'choices': [choice.to_dict() for choice in self.choices]
        }

# Add methods to Choice class
@staticmethod
def get_by_question_id(question_id: int) -> List[Choice]:
    """Lấy choices theo question_id"""
    try:
        query = "SELECT * FROM choices WHERE question_id = %s ORDER BY position"
        results = db.execute_query(query, (question_id,))
        choices = []
        for result in results:
            try:
                # Convert datetime to string if needed
                if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                    result['created_at'] = result['created_at'].isoformat()
                choices.append(Choice(**result))
            except Exception as e:
                logger.error(f"Error processing choice {result.get('id', 'unknown')}: {e}")
                continue
        return choices
    except Exception as e:
        logger.error(f"Error in get_by_question_id for question {question_id}: {e}")
        return []

Choice.get_by_question_id = get_by_question_id 