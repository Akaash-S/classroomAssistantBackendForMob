from flask import Blueprint, request, jsonify
from models import Notification, NotificationType, User, db
from datetime import datetime
import logging

notifications_bp = Blueprint('notifications', __name__)
logger = logging.getLogger(__name__)

@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    try:
        user_id = request.args.get('user_id')
        notification_type = request.args.get('type')
        is_read = request.args.get('is_read')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID is required'
            }), 400
        
        query = Notification.query.filter_by(user_id=user_id)
        
        if notification_type:
            try:
                type_enum = NotificationType(notification_type)
                query = query.filter_by(type=type_enum)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid notification type'
                }), 400
        
        if is_read is not None:
            query = query.filter_by(is_read=is_read.lower() == 'true')
        
        notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'notifications': [notification.to_dict() for notification in notifications],
            'total': query.count(),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Get notifications error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get notifications'
        }), 500

@notifications_bp.route('/', methods=['POST'])
def create_notification():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'type', 'title', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate notification type
        try:
            notification_type = NotificationType(data['type'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid notification type'
            }), 400
        
        # Verify user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Create new notification
        notification = Notification(
            user_id=data['user_id'],
            type=notification_type,
            title=data['title'],
            message=data['message'],
            data=data.get('data')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        logger.info(f"New notification created for user: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Notification created successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create notification error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create notification'
        }), 500

@notifications_bp.route('/<notification_id>', methods=['GET'])
def get_notification(notification_id):
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({
                'status': 'error',
                'message': 'Notification not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get notification error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get notification'
        }), 500

@notifications_bp.route('/<notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({
                'status': 'error',
                'message': 'Notification not found'
            }), 404
        
        notification.is_read = True
        db.session.commit()
        
        logger.info(f"Notification marked as read: {notification.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Notification marked as read',
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Mark notification as read error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to mark notification as read'
        }), 500

@notifications_bp.route('/<notification_id>/unread', methods=['PUT'])
def mark_as_unread(notification_id):
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({
                'status': 'error',
                'message': 'Notification not found'
            }), 404
        
        notification.is_read = False
        db.session.commit()
        
        logger.info(f"Notification marked as unread: {notification.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Notification marked as unread',
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Mark notification as unread error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to mark notification as unread'
        }), 500

@notifications_bp.route('/user/<user_id>/mark-all-read', methods=['PUT'])
def mark_all_as_read(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Mark all notifications for the user as read
        Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        logger.info(f"All notifications marked as read for user: {user.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'All notifications marked as read'
        }), 200
        
    except Exception as e:
        logger.error(f"Mark all notifications as read error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to mark all notifications as read'
        }), 500

@notifications_bp.route('/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    try:
        notification = Notification.query.get(notification_id)
        
        if not notification:
            return jsonify({
                'status': 'error',
                'message': 'Notification not found'
            }), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        logger.info(f"Notification deleted: {notification.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Notification deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete notification error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete notification'
        }), 500

@notifications_bp.route('/user/<user_id>/unread-count', methods=['GET'])
def get_unread_count(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        
        return jsonify({
            'status': 'success',
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        logger.error(f"Get unread count error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get unread count'
        }), 500
