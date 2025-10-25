#!/usr/bin/env python3
"""
Comprehensive test script for all backend endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("SUCCESS")
            return True
        else:
            print("FAILED")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def main():
    """Run comprehensive endpoint tests"""
    print("COMPREHENSIVE BACKEND ENDPOINT TEST")
    print("="*60)
    
    # Test basic health endpoints
    test_endpoint("GET", "/", description="Root health check")
    test_endpoint("GET", "/api/health", description="API health check")
    
    # Test authentication endpoints
    test_endpoint("GET", "/api/auth/test", description="Auth test endpoint")
    
    # Test lectures endpoints
    test_endpoint("GET", "/api/lectures/", description="Get all lectures")
    test_endpoint("POST", "/api/lectures/", 
                 data={"title": "Test Lecture", "subject": "Computer Science", "teacher_id": "test-teacher-id"},
                 description="Create new lecture")
    
    # Test tasks endpoints
    test_endpoint("GET", "/api/tasks/", description="Get all tasks")
    test_endpoint("POST", "/api/tasks/",
                 data={"title": "Test Task", "description": "Test task description", "assigned_to_id": "test-user-id"},
                 description="Create new task")
    
    # Test notifications endpoints
    test_endpoint("GET", "/api/notifications/", description="Get all notifications")
    test_endpoint("POST", "/api/notifications/",
                 data={"title": "Test Notification", "message": "Test notification message", "user_id": "test-user-id"},
                 description="Create new notification")
    
    # Test AI endpoints
    test_endpoint("POST", "/api/ai/transcribe",
                 data={"audio_url": "https://example.com/test-audio.mp3"},
                 description="Transcribe audio")
    test_endpoint("POST", "/api/ai/summarize",
                 data={"text": "This is a test text for summarization."},
                 description="Summarize text")
    
    print(f"\n{'='*60}")
    print("ENDPOINT TESTING COMPLETED")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
