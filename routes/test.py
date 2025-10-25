from flask import Blueprint, request, jsonify

test_bp = Blueprint('test', __name__)

@test_bp.route('/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        'status': 'success',
        'message': 'Test route working',
        'method': request.method,
        'data': request.get_json() if request.is_json else None
    })
