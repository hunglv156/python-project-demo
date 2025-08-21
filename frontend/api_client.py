import requests
import json
from typing import Dict, Any, List, Optional
from .config import config

class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.API_BASE_URL
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Add timeout to prevent hanging
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 10  # 10 seconds timeout
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception("API request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    # Authentication
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login user"""
        data = {"username": username, "password": password}
        return self._make_request("POST", "/auth/login", json=data)
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        return self._make_request("GET", f"/auth/user/{user_id}")
    
    # Subjects
    def get_subjects(self) -> List[Dict[str, Any]]:
        """Get all subjects"""
        return self._make_request("GET", "/subjects/")
    
    def get_subject(self, subject_id: int) -> Dict[str, Any]:
        """Get subject by ID"""
        return self._make_request("GET", f"/subjects/{subject_id}")
    
    def create_subject(self, name: str) -> Dict[str, Any]:
        """Create new subject"""
        return self._make_request("POST", "/subjects/", params={"name": name})
    
    # Questions
    def get_questions(self, subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get questions, optionally filtered by subject"""
        params = {}
        if subject_id:
            params["subject_id"] = subject_id
        return self._make_request("GET", "/questions/", params=params)
    
    def get_question(self, question_id: int) -> Dict[str, Any]:
        """Get question by ID"""
        return self._make_request("GET", f"/questions/{question_id}")
    
    def create_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new question"""
        return self._make_request("POST", "/questions/", json=question_data)
    
    def update_question(self, question_id: int, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update question"""
        return self._make_request("PUT", f"/questions/{question_id}", json=question_data)
    
    def delete_question(self, question_id: int) -> Dict[str, Any]:
        """Delete question"""
        return self._make_request("DELETE", f"/questions/{question_id}")
    
    # Exams
    def get_exams(self) -> List[Dict[str, Any]]:
        """Get all exams"""
        return self._make_request("GET", "/exams/")
    
    def get_exam(self, exam_id: int) -> Dict[str, Any]:
        """Get exam by ID"""
        return self._make_request("GET", f"/exams/{exam_id}")
    
    def create_exam(self, exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new exam"""
        return self._make_request("POST", "/exams/", json=exam_data)
    
    def add_exam_version(self, exam_id: int, question_ids: List[int]) -> Dict[str, Any]:
        """Add new version to exam"""
        return self._make_request("POST", f"/exams/{exam_id}/versions", json=question_ids)
    
    def get_exam_version(self, version_id: int) -> Dict[str, Any]:
        """Get exam version by ID"""
        return self._make_request("GET", f"/exams/versions/{version_id}")
    
    # Import DOCX
    def preview_docx(self, file_path: str) -> Dict[str, Any]:
        """Preview DOCX file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self._make_request("POST", "/import/preview", files=files)
    
    def import_docx(self, file_path: str, subject_id: int, created_by: int) -> Dict[str, Any]:
        """Import DOCX file"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'subject_id': subject_id,
                'created_by': created_by
            }
            return self._make_request("POST", "/import/docx", files=files, data=data) 