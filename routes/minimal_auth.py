from flask import Blueprint, request, jsonify, current_app
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        print("=== MINIMAL REGISTRATION ENDPOINT CALLED ===")
        data = request.get_json()
        print(f"Data received: {data}")
        
        # Just return success without database operations
        return jsonify({
            'status': 'success',
            'message': 'Registration endpoint working',
            'data': data
        }), 201
        
    except Exception as e:
        print(f"Error in registration: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500
