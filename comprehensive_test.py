#!/usr/bin/env python3
"""
Comprehensive test for the backend API
"""

import requests
import json
import time

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get("http://localhost:5000/")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_auth_test():
    """Test auth test endpoint"""
    try:
        response = requests.get("http://localhost:5000/api/auth/test")
        print(f"Auth test: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Auth test failed: {e}")
        return False

def test_registration():
    """Test user registration"""
    data = {
        "email": "test@example.com",
        "name": "Test User",
        "role": "student",
        "password": "test123"
    }
    
    try:
        print(f"Sending registration request with data: {json.dumps(data, indent=2)}")
        response = requests.post("http://localhost:5000/api/auth/register", json=data)
        print(f"Registration: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 201
    except Exception as e:
        print(f"Registration failed: {e}")
        return False

def main():
    print("Comprehensive Backend API Test")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test server health
    if not test_server_health():
        print("Server is not running!")
        return
    
    # Test auth test endpoint
    if not test_auth_test():
        print("Auth routes not working!")
        return
    
    # Test registration
    if test_registration():
        print("Registration successful!")
    else:
        print("Registration failed!")

if __name__ == '__main__':
    main()
