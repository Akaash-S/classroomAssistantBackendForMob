from flask import Blueprint, request, jsonify
from services.speech_to_text import SpeechToTextService
from services.gemini_service import GeminiService
from services.s3_storage import S3StorageService
from models import Lecture, Task, TaskPriority, db, User
from datetime import datetime
import logging
import os

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

# Initialize services
speech_to_text = SpeechToTextService()
gemini_service = GeminiService()
storage_service = S3StorageService()

@ai_bp.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        data = request.get_json()
        
        if 'audio_url' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Audio URL is required'
            }), 400
        
        # Transcribe audio using RapidAPI
        transcript = speech_to_text.transcribe_audio(data['audio_url'])
        
        if not transcript:
            return jsonify({
                'status': 'error',
                'message': 'Failed to transcribe audio'
            }), 500
        
        logger.info("Audio transcription completed successfully")
        
        return jsonify({
            'status': 'success',
            'transcript': transcript
        }), 200
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to transcribe audio'
        }), 500

@ai_bp.route('/summarize', methods=['POST'])
def summarize_text():
    try:
        data = request.get_json()
        
        if 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Text is required'
            }), 400
        
        # Generate summary using Gemini
        summary = gemini_service.generate_summary(data['text'])
        
        if not summary:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate summary'
            }), 500
        
        logger.info("Text summarization completed successfully")
        
        return jsonify({
            'status': 'success',
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Summarization error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to summarize text'
        }), 500

@ai_bp.route('/extract-tasks', methods=['POST'])
def extract_tasks():
    try:
        data = request.get_json()
        
        if 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Text is required'
            }), 400
        
        # Extract tasks using Gemini API
        tasks = []
        
        if gemini_service.is_available():
            logger.info("Using Gemini API for task extraction")
            tasks = gemini_service.extract_tasks(data['text'])
        else:
            return jsonify({
                'status': 'error',
                'message': 'Gemini service not available for task extraction'
            }), 503
        
        if tasks is None:
            tasks = []
        
        logger.info(f"Extracted {len(tasks)} tasks from text")
        
        return jsonify({
            'status': 'success',
            'tasks': tasks
        }), 200
        
    except Exception as e:
        logger.error(f"Task extraction error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to extract tasks'
        }), 500

@ai_bp.route('/process-lecture/<lecture_id>', methods=['POST'])
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
                'message': 'No audio file found for this lecture'
            }), 400
        
        # Step 1: Transcribe audio
        logger.info(f"Transcribing audio for lecture: {lecture.title}")
        transcript = speech_to_text.transcribe_audio(lecture.audio_url)
        
        if not transcript:
            return jsonify({
                'status': 'error',
                'message': 'Failed to transcribe audio'
            }), 500
        
        # Step 2: Generate summary
        logger.info(f"Generating summary for lecture: {lecture.title}")
        summary = gemini_service.generate_summary(transcript)
        
        if not summary:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate summary'
            }), 500
        
        # Step 3: Extract key points
        logger.info(f"Extracting key points for lecture: {lecture.title}")
        key_points = gemini_service.extract_key_points(transcript)
        
        # Step 4: Extract tasks using Gemini API
        logger.info(f"Extracting tasks for lecture: {lecture.title}")
        tasks_data = []
        
        if gemini_service.is_available():
            logger.info("Using Gemini API for task extraction")
            tasks_data = gemini_service.extract_tasks(transcript)
        else:
            logger.warning("Gemini service not available for task extraction")
        
        # Update lecture with processed data
        lecture.transcript = transcript
        lecture.summary = summary
        if key_points:
            lecture.key_points = ', '.join(key_points) if isinstance(key_points, list) else key_points
        lecture.is_processed = True
        lecture.updated_at = datetime.utcnow()
        
        # Create tasks from extracted data
        created_tasks = []
        if tasks_data:
            # Get all students to assign tasks to
            students = User.query.filter(User.role == 'student').all()
            
            if students:
                for task_data in tasks_data:
                    for student in students:
                        try:
                            # Parse priority
                            priority_str = task_data.get('priority', 'medium').lower()
                            if priority_str == 'high':
                                priority = TaskPriority.HIGH
                            elif priority_str == 'low':
                                priority = TaskPriority.LOW
                            else:
                                priority = TaskPriority.MEDIUM
                            
                            # Parse due date
                            due_date = None
                            if task_data.get('due_date'):
                                try:
                                    from datetime import datetime as dt
                                    due_date = dt.fromisoformat(task_data['due_date'])
                                except (ValueError, TypeError):
                                    due_date = None
                            
                            task = Task(
                                title=task_data.get('title', 'Extracted Task'),
                                description=task_data.get('description', ''),
                                lecture_id=lecture.id,
                                assigned_to_id=student.id,
                                priority=priority,
                                due_date=due_date,
                                is_ai_generated=True
                            )
                            db.session.add(task)
                            created_tasks.append(task)
                        except Exception as task_error:
                            logger.error(f"Error creating task: {str(task_error)}")
                            continue
            else:
                logger.warning("No students found to assign tasks to")
        
        db.session.commit()
        
        logger.info(f"Lecture processing completed: {lecture.title}, created {len(created_tasks)} tasks")
        
        return jsonify({
            'status': 'success',
            'message': 'Lecture processed successfully',
            'lecture': lecture.to_dict(),
            'created_tasks': [task.to_dict() for task in created_tasks]
        }), 200
        
    except Exception as e:
        logger.error(f"Process lecture error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to process lecture'
        }), 500

@ai_bp.route('/upload-audio', methods=['POST'])
def upload_audio():
    try:
        # In a real implementation, you would handle file upload here
        # and upload to Supabase storage
        data = request.get_json()
        
        if 'file_name' not in data or 'file_content' not in data:
            return jsonify({
                'status': 'error',
                'message': 'File name and content are required'
            }), 400
        
        # Upload to Supabase storage
        audio_url = storage_service.upload_audio(
            data['file_name'],
            data['file_content']
        )
        
        if not audio_url:
            return jsonify({
                'status': 'error',
                'message': 'Failed to upload audio file'
            }), 500
        
        logger.info(f"Audio file uploaded successfully: {data['file_name']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Audio uploaded successfully',
            'audio_url': audio_url
        }), 200
        
    except Exception as e:
        logger.error(f"Upload audio error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to upload audio'
        }), 500

@ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    try:
        # Check if all AI services are available
        services_status = {
            'speech_to_text': speech_to_text.is_available(),
            'gemini': gemini_service.is_available(),
            'storage': storage_service.is_available()
        }
        
        # Task extraction available if Gemini is available
        task_extraction_available = services_status['gemini']
        
        all_healthy = all(services_status.values())
        
        return jsonify({
            'status': 'success' if all_healthy else 'partial',
            'services': services_status,
            'task_extraction_available': task_extraction_available,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if all_healthy else 503
        
    except Exception as e:
        logger.error(f"AI health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'AI services health check failed'
        }), 500
