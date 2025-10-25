#!/usr/bin/env python3
"""
Simple API test script for Classroom Assistant Backend
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("Health check passed")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {str(e)}")
        return False

def test_api_health():
    """Test the API health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("API health check passed")
            return True
        else:
            print(f"API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"API health check failed: {str(e)}")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "role": "student",
            "password": "testpassword123",
            "student_id": "TEST001",
            "major": "Computer Science",
            "year": "Junior"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("User registration test passed")
            user_data = response.json()
            return user_data.get('user', {}).get('id')
        else:
            print(f"User registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"User registration failed: {str(e)}")
        return None

def test_lecture_creation(teacher_id):
    """Test lecture creation"""
    try:
        data = {
            "title": "Test Lecture",
            "subject": "Test Subject",
            "teacher_id": teacher_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/lectures",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("Lecture creation test passed")
            lecture_data = response.json()
            return lecture_data.get('lecture', {}).get('id')
        else:
            print(f"Lecture creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Lecture creation failed: {str(e)}")
        return None

def test_task_creation(lecture_id, student_id):
    """Test task creation"""
    try:
        data = {
            "title": "Test Task",
            "description": "This is a test task",
            "lecture_id": lecture_id,
            "assigned_to_id": student_id,
            "priority": "medium"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tasks",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("Task creation test passed")
            return True
        else:
            print(f"Task creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Task creation failed: {str(e)}")
        return False

def test_ai_health():
    """Test AI services health"""
    try:
        response = requests.get(f"{BASE_URL}/api/ai/health")
        if response.status_code == 200:
            print("AI services health check passed")
            return True
        else:
            print(f"AI services health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"AI services health check failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Testing Classroom Assistant Backend API")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_health_check():
        print("Server is not running. Please start the server first.")
        sys.exit(1)
    
    if not test_api_health():
        print("API is not healthy.")
        sys.exit(1)
    
    # Test user registration
    student_id = test_user_registration()
    if not student_id:
        print("User registration failed.")
        sys.exit(1)
    
    # Test lecture creation (using student as teacher for simplicity)
    lecture_id = test_lecture_creation(student_id)
    if not lecture_id:
        print("Lecture creation failed.")
        sys.exit(1)
    
    # Test task creation
    if not test_task_creation(lecture_id, student_id):
        print("Task creation failed.")
        sys.exit(1)
    
    # Test AI services
    test_ai_health()
    
    print("=" * 50)
    print("All basic tests completed!")
    print("\nNext steps:")
    print("1. Set up your environment variables")
    print("2. Test AI services with real data")
    print("3. Integrate with the frontend")

if __name__ == '__main__':
    main()
