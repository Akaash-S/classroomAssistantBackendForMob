from flask import Blueprint, request, jsonify
from models import ChatRoom, ChatMessage, User, db
from datetime import datetime
import logging

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

@chat_bp.route('/rooms', methods=['GET'])
def get_chat_rooms():
    """Get all chat rooms for a user"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id is required'
            }), 400
        
        # Get chat rooms where user is either teacher or student
        chat_rooms = ChatRoom.query.filter(
            (ChatRoom.teacher_id == user_id) | (ChatRoom.student_id == user_id)
        ).order_by(ChatRoom.last_message_at.desc().nullslast()).all()
        
        return jsonify({
            'status': 'success',
            'chat_rooms': [room.to_dict(current_user_id=user_id) for room in chat_rooms],
            'total': len(chat_rooms)
        }), 200
        
    except Exception as e:
        logger.error(f"Get chat rooms error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get chat rooms'
        }), 500

@chat_bp.route('/rooms', methods=['POST'])
def create_chat_room():
    """Create a new chat room between teacher and student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'teacher_id' not in data or 'student_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'teacher_id and student_id are required'
            }), 400
        
        teacher_id = data['teacher_id']
        student_id = data['student_id']
        
        # Verify users exist and have correct roles
        teacher = User.query.get(teacher_id)
        student = User.query.get(student_id)
        
        if not teacher or not student:
            return jsonify({
                'status': 'error',
                'message': 'Teacher or student not found'
            }), 404
        
        if teacher.role.value != 'teacher':
            return jsonify({
                'status': 'error',
                'message': 'First user must be a teacher'
            }), 400
        
        if student.role.value != 'student':
            return jsonify({
                'status': 'error',
                'message': 'Second user must be a student'
            }), 400
        
        # Check if chat room already exists
        existing_room = ChatRoom.query.filter_by(
            teacher_id=teacher_id,
            student_id=student_id
        ).first()
        
        if existing_room:
            return jsonify({
                'status': 'success',
                'message': 'Chat room already exists',
                'chat_room': existing_room.to_dict()
            }), 200
        
        # Create new chat room
        chat_room = ChatRoom(
            teacher_id=teacher_id,
            student_id=student_id
        )
        
        db.session.add(chat_room)
        db.session.commit()
        
        logger.info(f"New chat room created between teacher {teacher_id} and student {student_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Chat room created successfully',
            'chat_room': chat_room.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create chat room error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create chat room'
        }), 500

@chat_bp.route('/rooms/<room_id>', methods=['GET'])
def get_chat_room(room_id):
    """Get a specific chat room"""
    try:
        user_id = request.args.get('user_id')
        
        chat_room = ChatRoom.query.get(room_id)
        
        if not chat_room:
            return jsonify({
                'status': 'error',
                'message': 'Chat room not found'
            }), 404
        
        # Verify user is part of this chat room
        if user_id and user_id not in [chat_room.teacher_id, chat_room.student_id]:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access to chat room'
            }), 403
        
        return jsonify({
            'status': 'success',
            'chat_room': chat_room.to_dict(current_user_id=user_id)
        }), 200
        
    except Exception as e:
        logger.error(f"Get chat room error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get chat room'
        }), 500

@chat_bp.route('/rooms/<room_id>/messages', methods=['GET'])
def get_messages(room_id):
    """Get all messages in a chat room"""
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Verify chat room exists
        chat_room = ChatRoom.query.get(room_id)
        
        if not chat_room:
            return jsonify({
                'status': 'error',
                'message': 'Chat room not found'
            }), 404
        
        # Verify user is part of this chat room
        if user_id and user_id not in [chat_room.teacher_id, chat_room.student_id]:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access to chat room'
            }), 403
        
        # Get messages
        messages = ChatMessage.query.filter_by(
            chat_room_id=room_id
        ).order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        # Mark messages as read if user_id is provided
        if user_id:
            unread_messages = [msg for msg in messages if msg.sender_id != user_id and not msg.is_read]
            for msg in unread_messages:
                msg.is_read = True
            
            # Update unread count
            if user_id == chat_room.teacher_id:
                chat_room.unread_count_teacher = 0
            else:
                chat_room.unread_count_student = 0
            
            if unread_messages:
                db.session.commit()
        
        # Reverse to show oldest first
        messages.reverse()
        
        return jsonify({
            'status': 'success',
            'messages': [msg.to_dict() for msg in messages],
            'total': ChatMessage.query.filter_by(chat_room_id=room_id).count(),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Get messages error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get messages'
        }), 500

@chat_bp.route('/rooms/<room_id>/messages', methods=['POST'])
def send_message(room_id):
    """Send a message in a chat room"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'sender_id' not in data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'sender_id and message are required'
            }), 400
        
        sender_id = data['sender_id']
        message_text = data['message'].strip()
        
        if not message_text:
            return jsonify({
                'status': 'error',
                'message': 'Message cannot be empty'
            }), 400
        
        # Verify chat room exists
        chat_room = ChatRoom.query.get(room_id)
        
        if not chat_room:
            return jsonify({
                'status': 'error',
                'message': 'Chat room not found'
            }), 404
        
        # Verify sender is part of this chat room
        if sender_id not in [chat_room.teacher_id, chat_room.student_id]:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized to send message in this chat room'
            }), 403
        
        # Create message
        message = ChatMessage(
            chat_room_id=room_id,
            sender_id=sender_id,
            message=message_text
        )
        
        # Update chat room
        chat_room.last_message = message_text[:100]  # Store first 100 chars
        chat_room.last_message_at = datetime.utcnow()
        
        # Increment unread count for the other user
        if sender_id == chat_room.teacher_id:
            chat_room.unread_count_student += 1
        else:
            chat_room.unread_count_teacher += 1
        
        db.session.add(message)
        db.session.commit()
        
        logger.info(f"Message sent in chat room {room_id} by user {sender_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Message sent successfully',
            'chat_message': message.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to send message'
        }), 500

@chat_bp.route('/rooms/<room_id>/messages/<message_id>', methods=['DELETE'])
def delete_message(room_id, message_id):
    """Delete a message"""
    try:
        user_id = request.args.get('user_id')
        
        message = ChatMessage.query.get(message_id)
        
        if not message:
            return jsonify({
                'status': 'error',
                'message': 'Message not found'
            }), 404
        
        # Verify message belongs to this chat room
        if message.chat_room_id != room_id:
            return jsonify({
                'status': 'error',
                'message': 'Message does not belong to this chat room'
            }), 400
        
        # Verify user is the sender
        if user_id and message.sender_id != user_id:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized to delete this message'
            }), 403
        
        db.session.delete(message)
        db.session.commit()
        
        logger.info(f"Message {message_id} deleted from chat room {room_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Message deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete message error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete message'
        }), 500

@chat_bp.route('/rooms/<room_id>/mark-read', methods=['PUT'])
def mark_messages_read(room_id):
    """Mark all messages as read for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id is required'
            }), 400
        
        # Verify chat room exists
        chat_room = ChatRoom.query.get(room_id)
        
        if not chat_room:
            return jsonify({
                'status': 'error',
                'message': 'Chat room not found'
            }), 404
        
        # Verify user is part of this chat room
        if user_id not in [chat_room.teacher_id, chat_room.student_id]:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized access to chat room'
            }), 403
        
        # Mark all unread messages as read
        unread_messages = ChatMessage.query.filter_by(
            chat_room_id=room_id,
            is_read=False
        ).filter(ChatMessage.sender_id != user_id).all()
        
        for msg in unread_messages:
            msg.is_read = True
        
        # Reset unread count
        if user_id == chat_room.teacher_id:
            chat_room.unread_count_teacher = 0
        else:
            chat_room.unread_count_student = 0
        
        db.session.commit()
        
        logger.info(f"Messages marked as read in chat room {room_id} for user {user_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Messages marked as read',
            'marked_count': len(unread_messages)
        }), 200
        
    except Exception as e:
        logger.error(f"Mark messages read error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to mark messages as read'
        }), 500

@chat_bp.route('/rooms/<room_id>', methods=['DELETE'])
def delete_chat_room(room_id):
    """Delete a chat room and all its messages"""
    try:
        user_id = request.args.get('user_id')
        
        chat_room = ChatRoom.query.get(room_id)
        
        if not chat_room:
            return jsonify({
                'status': 'error',
                'message': 'Chat room not found'
            }), 404
        
        # Verify user is part of this chat room
        if user_id and user_id not in [chat_room.teacher_id, chat_room.student_id]:
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized to delete this chat room'
            }), 403
        
        db.session.delete(chat_room)
        db.session.commit()
        
        logger.info(f"Chat room {room_id} deleted")
        
        return jsonify({
            'status': 'success',
            'message': 'Chat room deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete chat room error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete chat room'
        }), 500

@chat_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """Get total unread message count for a user"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'user_id is required'
            }), 400
        
        # Get all chat rooms for user
        chat_rooms = ChatRoom.query.filter(
            (ChatRoom.teacher_id == user_id) | (ChatRoom.student_id == user_id)
        ).all()
        
        # Calculate total unread count
        total_unread = 0
        for room in chat_rooms:
            if user_id == room.teacher_id:
                total_unread += room.unread_count_teacher
            else:
                total_unread += room.unread_count_student
        
        return jsonify({
            'status': 'success',
            'unread_count': total_unread
        }), 200
        
    except Exception as e:
        logger.error(f"Get unread count error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get unread count'
        }), 500
