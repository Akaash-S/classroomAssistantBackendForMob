from flask import Blueprint, request, jsonify
from models import Lecture, User, db
from datetime import datetime
import logging

lectures_bp = Blueprint('lectures', __name__)
logger = logging.getLogger(__name__)

@lectures_bp.route('/', methods=['GET'])
def get_lectures():
    try:
        teacher_id = request.args.get('teacher_id')
        subject = request.args.get('subject')
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = Lecture.query
        
        if teacher_id:
            query = query.filter_by(teacher_id=teacher_id)
        
        if subject:
            query = query.filter(Lecture.subject.ilike(f'%{subject}%'))
        
        lectures = query.order_by(Lecture.created_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'lectures': [lecture.to_dict() for lecture in lectures],
            'total': query.count(),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Get lectures error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get lectures'
        }), 500

@lectures_bp.route('/', methods=['POST'])
def create_lecture():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'subject', 'teacher_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Verify teacher exists
        teacher = User.query.get(data['teacher_id'])
        if not teacher or teacher.role.value != 'teacher':
            return jsonify({
                'status': 'error',
                'message': 'Invalid teacher ID'
            }), 400
        
        # Create new lecture
        lecture = Lecture(
            title=data['title'],
            subject=data['subject'],
            teacher_id=data['teacher_id'],
            audio_url=data.get('audio_url'),
            audio_duration=data.get('audio_duration'),
            transcript=data.get('transcript'),
            summary=data.get('summary'),
            key_points=data.get('key_points'),
            tags=data.get('tags')
        )
        
        db.session.add(lecture)
        db.session.commit()
        
        logger.info(f"New lecture created: {lecture.title} by teacher: {teacher.email}")
        
        return jsonify({
            'status': 'success',
            'message': 'Lecture created successfully',
            'lecture': lecture.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create lecture error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create lecture'
        }), 500

@lectures_bp.route('/<lecture_id>', methods=['GET'])
def get_lecture(lecture_id):
    try:
        lecture = Lecture.query.get(lecture_id)
        
        if not lecture:
            return jsonify({
                'status': 'error',
                'message': 'Lecture not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'lecture': lecture.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get lecture error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get lecture'
        }), 500

@lectures_bp.route('/<lecture_id>', methods=['PUT'])
def update_lecture(lecture_id):
    try:
        lecture = Lecture.query.get(lecture_id)
        
        if not lecture:
            return jsonify({
                'status': 'error',
                'message': 'Lecture not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['title', 'subject', 'audio_url', 'audio_duration', 'transcript', 'summary', 'key_points', 'tags', 'is_processed']
        
        for field in allowed_fields:
            if field in data:
                setattr(lecture, field, data[field])
        
        lecture.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Lecture updated: {lecture.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Lecture updated successfully',
            'lecture': lecture.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update lecture error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update lecture'
        }), 500

@lectures_bp.route('/<lecture_id>', methods=['DELETE'])
def delete_lecture(lecture_id):
    try:
        lecture = Lecture.query.get(lecture_id)
        
        if not lecture:
            return jsonify({
                'status': 'error',
                'message': 'Lecture not found'
            }), 404
        
        # Delete lecture and related tasks
        db.session.delete(lecture)
        db.session.commit()
        
        logger.info(f"Lecture deleted: {lecture.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Lecture deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete lecture error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete lecture'
        }), 500

@lectures_bp.route('/<lecture_id>/upload-audio', methods=['POST'])
def upload_audio(lecture_id):
    try:
        lecture = Lecture.query.get(lecture_id)
        
        if not lecture:
            return jsonify({
                'status': 'error',
                'message': 'Lecture not found'
            }), 404
        
        # Check if file is uploaded
        if 'audio_file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio_file']
        
        if audio_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        # Validate file type
        allowed_extensions = {'mp3', 'wav', 'm4a', 'flac', 'ogg'}
        if not ('.' in audio_file.filename and 
                audio_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({
                'status': 'error',
                'message': 'Invalid file type. Allowed: mp3, wav, m4a, flac, ogg'
            }), 400
        
        # Generate unique filename
        import uuid
        file_extension = audio_file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{lecture_id}_{uuid.uuid4().hex}.{file_extension}"
        
        # Upload to Supabase storage
        from services.supabase_storage import SupabaseStorageService
        storage_service = SupabaseStorageService()
        
        logger.info(f"Storage service available: {storage_service.is_available()}")
        
        if not storage_service.is_available():
            logger.error("Storage service not available - check Supabase configuration")
            return jsonify({
                'status': 'error',
                'message': 'Storage service not available - check Supabase configuration'
            }), 500
        
        # Read file content
        file_content = audio_file.read()
        logger.info(f"File content size: {len(file_content)} bytes")
        
        if len(file_content) == 0:
            logger.error("File content is empty")
            return jsonify({
                'status': 'error',
                'message': 'File content is empty'
            }), 400
        
        # Upload to Supabase
        logger.info(f"Attempting to upload file: {unique_filename}")
        public_url = storage_service.upload_audio(unique_filename, file_content)
        
        if not public_url:
            logger.error("Upload failed - no public URL returned")
            return jsonify({
                'status': 'error',
                'message': 'Failed to upload file to storage - check backend logs for details'
            }), 500
        
        # Update lecture with audio URL
        lecture.audio_url = public_url
        lecture.audio_duration = request.form.get('audio_duration')  # Optional duration
        lecture.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Audio uploaded for lecture: {lecture.title} - URL: {public_url}")
        
        return jsonify({
            'status': 'success',
            'message': 'Audio uploaded successfully',
            'audio_url': public_url,
            'lecture': lecture.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Upload audio error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to upload audio'
        }), 500

@lectures_bp.route('/<lecture_id>/process', methods=['POST'])
def process_lecture(lecture_id):
    try:
        lecture = Lecture.query.get(lecture_id)
        
        if not lecture:
            return jsonify({
                'status': 'error',
                'message': 'Lecture not found'
            }), 404
        
        if not lecture.audio_url:
            return jsonify({
                'status': 'error',
                'message': 'No audio file uploaded for this lecture'
            }), 400
        
        # Initialize AI services
        from services.speech_to_text import SpeechToTextService
        from services.gemini_service import GeminiService
        
        speech_service = SpeechToTextService()
        gemini_service = GeminiService()
        
        transcript = None
        summary = None
        key_points = None
        
        # Step 1: Transcribe audio
        if speech_service.is_available():
            logger.info(f"Transcribing audio for lecture: {lecture.title}")
            transcript = speech_service.transcribe_audio(lecture.audio_url)
            
            if transcript:
                lecture.transcript = transcript
                logger.info(f"Transcription completed: {len(transcript)} characters")
            else:
                logger.warning("Transcription failed")
        else:
            logger.warning("Speech-to-text service not available")
        
        # Step 2: Generate summary and key points
        if gemini_service.is_available() and transcript:
            logger.info(f"Generating summary for lecture: {lecture.title}")
            
            # Generate summary
            summary = gemini_service.generate_summary(transcript)
            if summary:
                lecture.summary = summary
                logger.info(f"Summary generated: {len(summary)} characters")
            
            # Generate key points
            key_points_prompt = f"Extract the key points from this lecture transcript:\n\n{transcript}\n\nProvide 5-7 main points in bullet format."
            key_points = gemini_service.generate_summary(key_points_prompt)
            if key_points:
                lecture.key_points = key_points
                logger.info(f"Key points generated: {len(key_points)} characters")
        else:
            logger.warning("Gemini service not available or no transcript")
        
        # Mark lecture as processed
        lecture.is_processed = True
        lecture.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Lecture processed successfully: {lecture.title}")
        
        return jsonify({
            'status': 'success',
            'message': 'Lecture processed successfully',
            'lecture': lecture.to_dict(),
            'processing_results': {
                'transcript_generated': bool(transcript),
                'summary_generated': bool(summary),
                'key_points_generated': bool(key_points)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Process lecture error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to process lecture'
        }), 500
