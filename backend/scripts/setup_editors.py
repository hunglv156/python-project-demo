#!/usr/bin/env python3
"""
Script để tạo editor mới và phân công môn học
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.user_subject import UserSubject
from backend.models.user import User
from backend.models.subject import Subject
from backend.database import db

def create_editors():
    """Tạo các editor mới"""
    print("=== Tạo các editor mới ===")
    
    # Tạo editor 2 (user_id=4)
    try:
        query = "INSERT INTO users (id, username, password, role) VALUES (4, '4', '4', 'editor') ON CONFLICT (id) DO NOTHING"
        db.execute_query(query)
        print("✓ Tạo editor 2 (user_id=4, username=4)")
    except Exception as e:
        print(f"✗ Lỗi tạo editor 2: {e}")
    
    # Tạo editor 3 (user_id=5)
    try:
        query = "INSERT INTO users (id, username, password, role) VALUES (5, '5', '5', 'editor') ON CONFLICT (id) DO NOTHING"
        db.execute_query(query)
        print("✓ Tạo editor 3 (user_id=5, username=5)")
    except Exception as e:
        print(f"✗ Lỗi tạo editor 3: {e}")

def assign_subjects():
    """Phân công môn học cho các editor"""
    print("\n=== Phân công môn học ===")
    
    # Lấy danh sách môn học
    subjects = Subject.get_all()
    subject_map = {}
    for subject in subjects:
        subject_map[subject.name] = subject.id
    
    # Phân công môn học
    assignments = [
        # Editor 1 (user_id=2): Toán học cơ bản, Tiếng Việt
        (2, "Toán học cơ bản"),
        (2, "Tiếng Việt"),
        
        # Editor 2 (user_id=4): Khoa học tự nhiên, Lịch sử Việt Nam
        (4, "Khoa học tự nhiên"),
        (4, "Lịch sử Việt Nam"),
        
        # Editor 3 (user_id=5): Địa lý Việt Nam, Tiếng Anh cơ bản
        (5, "Địa lý Việt Nam"),
        (5, "Tiếng Anh cơ bản")
    ]
    
    for user_id, subject_name in assignments:
        if subject_name in subject_map:
            subject_id = subject_map[subject_name]
            success = UserSubject.assign_subject_to_user(user_id, subject_id)
            if success:
                print(f"✓ Phân công '{subject_name}' cho editor {user_id}")
            else:
                print(f"✗ Lỗi phân công '{subject_name}' cho editor {user_id}")
        else:
            print(f"✗ Không tìm thấy môn học '{subject_name}'")

def verify_assignments():
    """Kiểm tra phân công"""
    print("\n=== Kiểm tra phân công ===")
    
    editors = [2, 4, 5]
    for user_id in editors:
        user = User.get_by_id(user_id)
        if user:
            print(f"\nEditor {user_id} ({user.username}):")
            subject_ids = UserSubject.get_user_subjects(user_id)
            for subject_id in subject_ids:
                subject = Subject.get_by_id(subject_id)
                if subject:
                    print(f"  - {subject.name}")
        else:
            print(f"✗ Không tìm thấy user {user_id}")

def test_permissions():
    """Test quyền truy cập"""
    print("\n=== Test quyền truy cập ===")
    
    # Test editor 1 với môn Toán (có quyền)
    has_access = UserSubject.user_has_subject_access(2, 1)  # Toán học
    print(f"Editor 1 có quyền truy cập Toán học: {has_access}")
    
    # Test editor 1 với môn Khoa học (không có quyền)
    has_access = UserSubject.user_has_subject_access(2, 3)  # Khoa học
    print(f"Editor 1 có quyền truy cập Khoa học: {has_access}")
    
    # Test editor 2 với môn Khoa học (có quyền)
    has_access = UserSubject.user_has_subject_access(4, 3)  # Khoa học
    print(f"Editor 2 có quyền truy cập Khoa học: {has_access}")

if __name__ == "__main__":
    print("=== Thiết lập hệ thống phân quyền ===")
    try:
        # Kết nối database
        db.connect()
        
        # Tạo editor mới
        create_editors()
        
        # Phân công môn học
        assign_subjects()
        
        # Kiểm tra phân công
        verify_assignments()
        
        # Test quyền truy cập
        test_permissions()
        
        print("\n=== Hoàn thành thiết lập ===")
        print("\nThông tin đăng nhập:")
        print("- Editor 1: username=2, password=2")
        print("- Editor 2: username=4, password=4") 
        print("- Editor 3: username=5, password=5")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Đóng kết nối database
        db.close() 