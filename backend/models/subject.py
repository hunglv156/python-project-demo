from typing import List, Dict, Any
from ..database import db

class Subject:
    def __init__(self, id: int, name: str, created_at: str):
        self.id = id
        self.name = name
        self.created_at = created_at
    
    @staticmethod
    def get_all() -> List['Subject']:
        """Lấy tất cả subjects"""
        query = "SELECT * FROM subjects ORDER BY name"
        results = db.execute_query(query)
        subjects = []
        for result in results:
            # Convert datetime to string if it's a datetime object
            if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                result['created_at'] = result['created_at'].isoformat()
            subjects.append(Subject(**result))
        return subjects
    
    @staticmethod
    def get_by_id(subject_id: int) -> 'Subject':
        """Lấy subject theo ID"""
        query = "SELECT * FROM subjects WHERE id = %s"
        result = db.execute_single(query, (subject_id,))
        if result:
            # Convert datetime to string if it's a datetime object
            if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                result['created_at'] = result['created_at'].isoformat()
            return Subject(**result)
        return None
    
    @staticmethod
    def create(name: str) -> 'Subject':
        """Tạo subject mới"""
        query = "INSERT INTO subjects (name) VALUES (%s) RETURNING *"
        result = db.execute_single(query, (name,))
        if result:
            # Convert datetime to string if it's a datetime object
            if 'created_at' in result and hasattr(result['created_at'], 'isoformat'):
                result['created_at'] = result['created_at'].isoformat()
            return Subject(**result)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subject thành dict"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': str(self.created_at) if self.created_at else None
        } 