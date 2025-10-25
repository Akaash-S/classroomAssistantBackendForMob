from flask import Blueprint, request, jsonify, current_app
from models import User, UserRole
from datetime import datetime
import logging

# Import db from the main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import db

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/test', methods=['GET'])
def test():
    try:
        print("=== TEST ROUTE CALLED ===")
        print("Database obtained")
        
        # Test database connection
        db.session.execute(db.text("SELECT 1"))
        print("Database connection test successful")
        
        # Test User model creation
        test_user = User(
            firebase_uid="test_uid",
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT
        )
        print("User model created successfully")
        
        return jsonify({
            'status': 'success',
            'message': 'Test route working',
            'user_id': test_user.id,
            'firebase_uid': test_user.firebase_uid
        }), 200
        
    except Exception as e:
        print(f"Test route error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}'
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        print("=== FIREBASE AUTH REGISTRATION CALLED ===")
        data = request.get_json()
        print(f"Data: {data}")
        
        # Validate required fields (no password needed with Firebase)
        required_fields = ['email', 'name', 'role', 'firebase_uid']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Get database from current app context
        print("Getting database...")
        print("Database obtained")
        
        # Test database connection
        try:
            db.session.execute(db.text("SELECT 1"))
            print("Database connection test successful")
        except Exception as db_error:
            print(f"Database connection test failed: {str(db_error)}")
            raise db_error
        
        # Check if user already exists by email or firebase_uid
        print("Checking existing user...")
        existing_user = User.query.filter(
            (User.email == data['email']) | 
            (User.firebase_uid == data['firebase_uid'])
        ).first()
        
        if existing_user:
            print("User exists")
            return jsonify({
                'status': 'error',
                'message': 'User with this email or Firebase UID already exists'
            }), 409
        
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role. Must be "teacher" or "student"'
            }), 400
        
        # Create new user with Firebase UID
        print("Creating new user...")
        user = User(
            firebase_uid=data['firebase_uid'],
            email=data['email'],
            name=data['name'],
            role=role,
            student_id=data.get('student_id'),
            major=data.get('major'),
            year=data.get('year'),
            department=data.get('department'),
            bio=data.get('bio'),
            phone=data.get('phone')
        )
        
        print("Adding user to session...")
        db.session.add(user)
        
        print("Committing to database...")
        db.session.commit()
        
        print("User created successfully!")
        logger.info(f"New user registered: {user.email} with role: {user.role.value} and Firebase UID: {user.firebase_uid}")
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            db = current_app.extensions['sqlalchemy'].db
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': 'Registration failed'
        }), 500
