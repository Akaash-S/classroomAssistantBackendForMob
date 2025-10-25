#!/usr/bin/env python3
"""
Simple test script for Firebase authentication backend
"""

import requests
import json
import uuid

# Backend URL
BASE_URL = "http://localhost:5000/api/auth"

def test_health_check():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code == 200:
            print("Backend is running and healthy")
            return True
        else:
            print(f"Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Cannot connect to backend: {str(e)}")
        return False

def test_user_registration():
    """Test user registration with Firebase UID"""
    print("\nTesting user registration...")
    
    # Generate test data
    test_firebase_uid = f"test_firebase_uid_{uuid.uuid4()}"
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    registration_data = {
        "firebase_uid": test_firebase_uid,
        "email": test_email,
        "name": "Test User",
        "role": "student",
        "student_id": "STU001",
        "major": "Computer Science",
        "year": "2024"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print("User registration successful")
            print(f"User ID: {data['user']['id']}")
            print(f"Firebase UID: {data['user']['firebase_uid']}")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            return test_firebase_uid, data['user']['id']
        else:
            print(f"Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return None, None

def test_user_login(firebase_uid):
    """Test user login with Firebase UID"""
    print("\nTesting user login...")
    
    login_data = {
        "firebase_uid": firebase_uid
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("User login successful")
            print(f"User ID: {data['user']['id']}")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            return True
        else:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Starting Firebase Authentication Backend Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\nBackend is not running. Please start the backend first.")
        return
    
    # Test 2: User registration
    firebase_uid, user_id = test_user_registration()
    if not firebase_uid:
        print("\nRegistration test failed. Stopping tests.")
        return
    
    # Test 3: User login
    if not test_user_login(firebase_uid):
        print("\nLogin test failed.")
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == '__main__':
    main()