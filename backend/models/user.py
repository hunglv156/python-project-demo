from typing import Optional, Dict, Any
import bcrypt
from ..database import db

class User:
    def __init__(self, id: int, username: str, password: str, role: str, created_at: str):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password với bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        return password == self.password
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional['User']:
        """Xác thực user"""
        query = "SELECT * FROM users WHERE username = %s"
        result = db.execute_single(query, (username,))
        
        if result:
            user = User(**result)
            if user.verify_password(password):
                return user
        return None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Lấy user theo ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = db.execute_single(query, (user_id,))
        return User(**result) if result else None
    
    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        """Lấy user theo username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = db.execute_single(query, (username,))
        return User(**result) if result else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user thành dict"""
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at
        } 