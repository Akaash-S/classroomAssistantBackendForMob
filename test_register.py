#!/usr/bin/env python3
"""
Test registration endpoint directly
"""

import requests
import json

def test_registration():
    """Test the registration endpoint"""
    url = "http://localhost:5000/api/auth/register"
    
    data = {
        "email": "test@example.com",
        "name": "Test User",
        "role": "student",
        "password": "test123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing registration endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("Registration successful!")
            return True
        else:
            print("Registration failed!")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_registration()
