#!/usr/bin/env python3
"""
Debug script for authentication issues
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Load environment variables
load_dotenv()

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    return app

def test_user_creation():
    """Test user creation directly"""
    print("Testing User Creation...")
    print("=" * 30)
    
    # Create Flask app
    app = create_app()
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    # Import models
    from models import User, UserRole
    
    try:
        with app.app_context():
            print("Creating test user...")
            
            # Create test user
            user = User(
                email="debug@example.com",
                name="Debug User",
                role=UserRole.STUDENT,
                student_id="DEBUG001",
                major="Computer Science",
                year="Senior"
            )
            
            print("Adding user to session...")
            db.session.add(user)
            
            print("Committing to database...")
            db.session.commit()
            
            print("User created successfully!")
            print(f"User ID: {user.id}")
            print(f"User Email: {user.email}")
            print(f"User Role: {user.role.value}")
            
            # Test to_dict method
            print("\nTesting to_dict method...")
            user_dict = user.to_dict()
            print(f"User dict: {user_dict}")
            
            return True
            
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("Debug Authentication Issues")
    print("=" * 30)
    
    if test_user_creation():
        print("\nUser creation test passed!")
    else:
        print("\nUser creation test failed!")

if __name__ == '__main__':
    main()
