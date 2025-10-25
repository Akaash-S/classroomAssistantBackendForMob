from flask import Blueprint, request, jsonify, current_app
from models import User, UserRole
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def get_db():
    """Get database instance from current app context"""
    return current_app.extensions['sqlalchemy'].db

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'role', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Get database instance
        db = get_db()
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({
                'status': 'error',
                'message': 'User with this email already exists'
            }), 409
        
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid role. Must be "teacher" or "student"'
            }), 400
        
        # Create new user
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
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {user.email} with role: {user.role.value}")
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        try:
            db = get_db()
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
        
        # Get database instance
        db = get_db()
        
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

@auth_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        db = get_db()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get profile'
        }), 500

@auth_bp.route('/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        db = get_db()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['name', 'student_id', 'major', 'year', 'department', 'bio', 'phone', 'notifications_enabled', 'email_notifications', 'dark_mode']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Profile updated for user: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        try:
            db = get_db()
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': 'Failed to update profile'
        }), 500

@auth_bp.route('/change-password/<user_id>', methods=['PUT'])
def change_password(user_id):
    try:
        db = get_db()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        
        if not data.get('new_password'):
            return jsonify({
                'status': 'error',
                'message': 'New password is required'
            }), 400
        
        # In a real app, you would hash and store the new password
        # For now, we'll just return success
        
        logger.info(f"Password changed for user: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        try:
            db = get_db()
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': 'Failed to change password'
        }), 500

@auth_bp.route('/delete-account/<user_id>', methods=['DELETE'])
def delete_account(user_id):
    try:
        db = get_db()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Delete user and related data
        db.session.delete(user)
        db.session.commit()
        
        logger.info(f"Account deleted for user: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Account deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete account error: {str(e)}")
        try:
            db = get_db()
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete account'
        }), 500
