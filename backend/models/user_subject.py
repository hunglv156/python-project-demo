from typing import List, Dict, Any
from ..database import db

class UserSubject:
    def __init__(self, user_id: int, subject_id: int):
        self.user_id = user_id
        self.subject_id = subject_id
    
    @staticmethod
    def assign_subject_to_user(user_id: int, subject_id: int) -> bool:
        """Phân công môn học cho user"""
        try:
            query = "INSERT INTO user_subjects (user_id, subject_id) VALUES (%s, %s) ON CONFLICT DO NOTHING"
            db.execute_query(query, (user_id, subject_id))
            return True
        except Exception as e:
            print(f"Error assigning subject to user: {e}")
            return False
    
    @staticmethod
    def get_user_subjects(user_id: int) -> List[int]:
        """Lấy danh sách subject_id mà user được phân công"""
        try:
            query = "SELECT subject_id FROM user_subjects WHERE user_id = %s"
            results = db.execute_query(query, (user_id,))
            return [row['subject_id'] for row in results]
        except Exception as e:
            print(f"Error getting user subjects: {e}")
            return []
    
    @staticmethod
    def user_has_subject_access(user_id: int, subject_id: int) -> bool:
        """Kiểm tra user có quyền truy cập subject không"""
        try:
            query = "SELECT 1 FROM user_subjects WHERE user_id = %s AND subject_id = %s"
            result = db.execute_single(query, (user_id, subject_id))
            return result is not None
        except Exception as e:
            print(f"Error checking user subject access: {e}")
            return False
    
    @staticmethod
    def get_all_assignments() -> List[Dict[str, Any]]:
        """Lấy tất cả phân công môn học"""
        try:
            query = """
                SELECT us.user_id, us.subject_id, u.username, s.name as subject_name
                FROM user_subjects us
                JOIN users u ON us.user_id = u.id
                JOIN subjects s ON us.subject_id = s.id
                ORDER BY u.username, s.name
            """
            results = db.execute_query(query)
            return results
        except Exception as e:
            print(f"Error getting all assignments: {e}")
            return [] 