from flask import Blueprint, request, jsonify
from models import User, UserRole
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        print("Registration endpoint called")
        data = request.get_json()
        print(f"Received data: {data}")
        
        # Validate required fields
        required_fields = ['email', 'name', 'role', 'password']
        for field in required_fields:
            if field not in data:
                print(f"Missing field: {field}")
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Get database from current app context
        print("Getting database from app context...")
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        print("Database obtained successfully")
        
        # Check if user already exists
        print("Checking if user already exists...")
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            print("User already exists")
            return jsonify({
                'status': 'error',
                'message': 'User with this email already exists'
            }), 409
        
        # Validate role
        print("Validating role...")
        try:
            role = UserRole(data['role'])
            print(f"Role validated: {role.value}")
        except ValueError:
            print("Invalid role")
            return jsonify({
                'status': 'error',
                'message': 'Invalid role. Must be "teacher" or "student"'
            }), 400
        
        # Create new user
        print("Creating new user...")
        user = User(
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
        print("User object created")
        
        print("Adding user to session...")
        db.session.add(user)
        print("User added to session")
        
        print("Committing to database...")
        db.session.commit()
        print("User committed to database")
        
        logger.info(f"New user registered: {user.email} with role: {user.role.value}")
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        try:
            from flask import current_app
            db = current_app.extensions['sqlalchemy'].db
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': 'Registration failed'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({
                'status': 'error',
                'message': 'Email is required'
            }), 400
        
        # Get database from current app context
        from flask import current_app
        db = current_app.extensions['sqlalchemy'].db
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401
        
        # In a real app, you would verify the password here
        # For now, we'll just return the user data
        
        logger.info(f"User logged in: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Login failed'
        }), 500
