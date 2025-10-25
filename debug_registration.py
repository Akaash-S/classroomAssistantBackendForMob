#!/usr/bin/env python3
"""
Simple test script to debug registration
"""

import requests
import json
import uuid

def test_registration():
    """Test user registration with detailed error reporting"""
    print("Testing user registration...")
    
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
        print(f"Sending request to: http://localhost:5000/api/auth/register")
        print(f"Data: {json.dumps(registration_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:5000/api/auth/register",
            json=registration_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            print("SUCCESS: User registration successful")
            print(f"User ID: {data['user']['id']}")
            print(f"Firebase UID: {data['user']['firebase_uid']}")
            print(f"Email: {data['user']['email']}")
            print(f"Role: {data['user']['role']}")
            return True
        else:
            print(f"FAILED: Registration failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"CONNECTION ERROR: Cannot connect to server: {str(e)}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"TIMEOUT ERROR: Request timed out: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    test_registration()
