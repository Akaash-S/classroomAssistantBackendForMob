from flask import Blueprint, request, jsonify, current_app
from models import User, UserRole
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/test', methods=['GET'])
def test():
    try:
        print("=== TEST ROUTE CALLED ===")
        
        # Get database from current app context
        db = current_app.extensions['sqlalchemy']
        
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
        
        print("Getting database...")
        
        # Get database from current app context
        db = current_app.extensions['sqlalchemy']
        
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
        
        if not data.get('firebase_uid'):
            return jsonify({
                'status': 'error',
                'message': 'Firebase UID is required'
            }), 400
        
        # Find user by Firebase UID
        user = User.query.filter_by(firebase_uid=data['firebase_uid']).first()
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        logger.info(f"User logged in: {user.email} with Firebase UID: {user.firebase_uid}")
        
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

@auth_bp.route('/user/firebase/<firebase_uid>', methods=['GET'])
def get_user_by_firebase_uid(firebase_uid):
    try:
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
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
        logger.error(f"Get user by Firebase UID error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get user'
        }), 500

@auth_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users, optionally filtered by role"""
    try:
        role_filter = request.args.get('role')
        
        query = User.query
        
        # Filter by role if provided
        if role_filter:
            try:
                role = UserRole(role_filter)
                query = query.filter_by(role=role)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid role. Must be "teacher" or "student"'
                }), 400
        
        users = query.order_by(User.name).all()
        
        return jsonify({
            'status': 'success',
            'users': [user.to_dict() for user in users],
            'total': len(users)
        }), 200
        
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get users'
        }), 500

@auth_bp.route('/user/update/<firebase_uid>', methods=['PUT'])
def update_user_profile(firebase_uid):
    try:
        data = request.get_json()
        
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Get database from current app context
        db = current_app.extensions['sqlalchemy']
        
        # Update user fields
        if 'name' in data:
            user.name = data['name']
        if 'student_id' in data:
            user.student_id = data['student_id']
        if 'major' in data:
            user.major = data['major']
        if 'year' in data:
            user.year = data['year']
        if 'department' in data:
            user.department = data['department']
        if 'bio' in data:
            user.bio = data['bio']
        if 'phone' in data:
            user.phone = data['phone']
        if 'notifications_enabled' in data:
            user.notifications_enabled = data['notifications_enabled']
        if 'email_notifications' in data:
            user.email_notifications = data['email_notifications']
        if 'dark_mode' in data:
            user.dark_mode = data['dark_mode']
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User profile updated: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({
            'status': 'error',
            'message': 'Failed to update profile'
        }), 500