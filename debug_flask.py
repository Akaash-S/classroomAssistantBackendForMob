#!/usr/bin/env python3
"""
Debug script to test Flask app and model
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, UserRole

def test_flask_app():
    """Test Flask app and model"""
    try:
        with app.app_context():
            print("Flask app context created successfully")
            
            # Test database connection
            result = db.session.execute(db.text("SELECT 1"))
            print("Database session working")
            
            # Test User model
            print("Testing User model...")
            
            # Create a test user
            test_user = User(
                firebase_uid="test_debug_uid",
                email="debug@test.com",
                name="Debug User",
                role=UserRole.STUDENT
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
            
    except Exception as e:
        print(f"Flask app test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_flask_app()
