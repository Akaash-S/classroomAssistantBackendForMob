from flask import Blueprint, jsonify, request
from models import Lecture, Task, db
from services.background_processor import background_processor
import logging

logger = logging.getLogger(__name__)

processing_bp = Blueprint('processing', __name__)

@processing_bp.route('/process/status', methods=['GET'])
def get_processing_status():
    """Get the current processing status"""
    try:
        status = background_processor.get_processing_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get processing status'
        }), 500

@processing_bp.route('/process/start', methods=['POST'])
def start_processing():
    """Start background processing"""
    try:
        background_processor.start()
        return jsonify({
            'status': 'success',
            'message': 'Background processing started'
        })
    except Exception as e:
        logger.error(f"Error starting processing: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to start processing'
        }), 500

@processing_bp.route('/process/stop', methods=['POST'])
def stop_processing():
    """Stop background processing"""
    try:
        background_processor.stop()
        return jsonify({
            'status': 'success',
            'message': 'Background processing stopped'
        })
    except Exception as e:
        logger.error(f"Error stopping processing: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to stop processing'
        }), 500

@processing_bp.route('/process/lecture/<lecture_id>', methods=['POST'])
def process_lecture_immediately(lecture_id):
    """Process a specific lecture immediately"""
    try:
        result = background_processor.process_lecture_immediately(lecture_id)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'lecture_id': result.get('lecture_id')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing lecture immediately: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to process lecture'
        }), 500

@processing_bp.route('/process/unprocessed', methods=['GET'])
def get_unprocessed_lectures():
    """Get list of unprocessed lectures"""
    try:
        unprocessed = Lecture.query.filter(
            Lecture.audio_url.isnot(None),
            Lecture.is_processed == False
        ).all()
        
        lectures_data = []
        for lecture in unprocessed:
            lectures_data.append({
                'id': lecture.id,
                'title': lecture.title,
                'subject': lecture.subject,
                'created_at': lecture.created_at.isoformat() if lecture.created_at else None,
                'audio_url': lecture.audio_url,
                'teacher_id': lecture.teacher_id
            })
            
        return jsonify({
            'status': 'success',
            'data': {
                'lectures': lectures_data,
                'count': len(lectures_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting unprocessed lectures: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get unprocessed lectures'
        }), 500

@processing_bp.route('/process/retry-failed', methods=['POST'])
def retry_failed_processing():
    """Retry processing for lectures that failed"""
    try:
        # Find lectures that have been processing for too long (older than 1 hour)
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        failed_lectures = Lecture.query.filter(
            Lecture.audio_url.isnot(None),
            Lecture.is_processed == False,
            Lecture.updated_at < cutoff_time
        ).all()
        
        processed_count = 0
        for lecture in failed_lectures:
            try:
                result = background_processor.process_lecture_immediately(lecture.id)
                if result['success']:
                    processed_count += 1
            except Exception as e:
                logger.error(f"Failed to retry processing lecture {lecture.id}: {str(e)}")
                continue
                
        return jsonify({
            'status': 'success',
            'message': f'Retried processing for {processed_count} lectures'
        })
        
    except Exception as e:
        logger.error(f"Error retrying failed processing: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retry processing'
        }), 500
