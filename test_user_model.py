#!/usr/bin/env python3
"""
Test script to check User model and database operations
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, UserRole

def test_user_creation():
    """Test User model creation and database operations"""
    try:
        with app.app_context():
            print("Testing User model creation...")
            
            # Create a test user
            test_user = User(
                firebase_uid="test_debug_uid_123",
                email="debug@test.com",
                name="Debug User",
                role=UserRole.STUDENT,
                student_id="STU001",
                major="Computer Science",
                year="2024"
            )
            
            print("User model created successfully")
            print(f"User ID: {test_user.id}")
            print(f"Firebase UID: {test_user.firebase_uid}")
            print(f"Email: {test_user.email}")
            print(f"Role: {test_user.role}")
            
            # Test to_dict method
            user_dict = test_user.to_dict()
            print("to_dict method working")
            print(f"User dict keys: {list(user_dict.keys())}")
            
            # Test database operations
            print("Testing database operations...")
            
            # Check if user already exists
            existing_user = User.query.filter(
                (User.email == test_user.email) | 
                (User.firebase_uid == test_user.firebase_uid)
            ).first()
            
            if existing_user:
                print("User already exists in database")
                print(f"Existing user ID: {existing_user.id}")
            else:
                print("User does not exist, adding to database...")
                db.session.add(test_user)
                db.session.commit()
                print("User added to database successfully!")
                print(f"New user ID: {test_user.id}")
            
            return True
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_user_creation()
