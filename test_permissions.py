#!/usr/bin/env python3
"""
Script test chức năng phân quyền
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login(username, password):
    """Test đăng nhập"""
    print(f"\n=== Test đăng nhập với {username} ===")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        if data['success']:
            print(f"User: {data['user']}")
        return data['success']
    else:
        print(f"Error: {response.text}")
        return False

def test_subjects():
    """Test danh sách môn học"""
    print(f"\n=== Test danh sách môn học ===")
    
    response = requests.get(f"{BASE_URL}/subjects")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        subjects = response.json()
        print(f"Total subjects: {len(subjects)}")
        for subject in subjects:
            print(f"  - {subject['name']} (ID: {subject['id']})")
    else:
        print(f"Error: {response.text}")

def test_questions():
    """Test danh sách câu hỏi"""
    print(f"\n=== Test danh sách câu hỏi ===")
    
    response = requests.get(f"{BASE_URL}/questions")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        questions = response.json()
        print(f"Total questions: {len(questions)}")
        if questions:
            print(f"First question: {questions[0]['question'][:50]}...")
    else:
        print(f"Error: {response.text}")

def test_questions_by_subject(subject_id):
    """Test câu hỏi theo môn học"""
    print(f"\n=== Test câu hỏi môn học {subject_id} ===")
    
    response = requests.get(f"{BASE_URL}/questions?subject_id={subject_id}")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        questions = response.json()
        print(f"Total questions: {len(questions)}")
        if questions:
            print(f"First question: {questions[0]['question'][:50]}...")
    else:
        print(f"Error: {response.text}")

def test_logout():
    """Test đăng xuất"""
    print(f"\n=== Test đăng xuất ===")
    
    response = requests.post(f"{BASE_URL}/auth/logout")
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
    else:
        print(f"Error: {response.text}")

def main():
    """Test chính"""
    print("=== Test chức năng phân quyền ===")
    
    # Test đăng nhập với editor 1
    if test_login("2", "2"):
        # Test các chức năng
        test_subjects()
        test_questions()
        test_questions_by_subject(1)  # Toán học
        test_questions_by_subject(3)  # Khoa học (không có quyền)
        test_logout()
    
    print("\n" + "="*50)
    
    # Test đăng nhập với editor 2
    if test_login("4", "4"):
        # Test các chức năng
        test_subjects()
        test_questions()
        test_questions_by_subject(3)  # Khoa học
        test_questions_by_subject(1)  # Toán học (không có quyền)
        test_logout()
    
    print("\n" + "="*50)
    
    # Test đăng nhập với editor 3
    if test_login("5", "5"):
        # Test các chức năng
        test_subjects()
        test_questions()
        test_questions_by_subject(5)  # Địa lý
        test_questions_by_subject(1)  # Toán học (không có quyền)
        test_logout()
    
    print("\n=== Test hoàn thành ===")

if __name__ == "__main__":
    main() 