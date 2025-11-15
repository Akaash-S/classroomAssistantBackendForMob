import os
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional
from models import Lecture, Task, TaskPriority, db
from services.speech_to_text import SpeechToTextService
from services.gemini_service import GeminiService
from services.s3_storage import S3StorageService

logger = logging.getLogger(__name__)

class BackgroundProcessor:
    def __init__(self):
        self.speech_to_text = SpeechToTextService()
        self.gemini_service = GeminiService()
        self.storage_service = S3StorageService()
        self.is_running = False
        self.thread = None
        self.processing_interval = 300  # 5 minutes
        
    def start(self):
        """Start the background processing thread"""
        if self.is_running:
            logger.warning("Background processor is already running")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info("Background processor started")
        
    def stop(self):
        """Stop the background processing thread"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Background processor stopped")
        
    def _process_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                self._process_unprocessed_lectures()
                time.sleep(self.processing_interval)
            except Exception as e:
                logger.error(f"Error in background processing loop: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retrying
                
    def _process_unprocessed_lectures(self):
        """Process lectures that haven't been processed yet"""
        try:
            # Find lectures with audio but not processed
            unprocessed_lectures = Lecture.query.filter(
                Lecture.audio_url.isnot(None),
                Lecture.is_processed == False
            ).limit(5).all()  # Process max 5 at a time
            
            if not unprocessed_lectures:
                logger.debug("No unprocessed lectures found")
                return
                
            logger.info(f"Found {len(unprocessed_lectures)} unprocessed lectures")
            
            for lecture in unprocessed_lectures:
                try:
                    self._process_lecture(lecture)
                except Exception as e:
                    logger.error(f"Failed to process lecture {lecture.id}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing unprocessed lectures: {str(e)}")
            
    def _process_lecture(self, lecture: Lecture):
        """Process a single lecture"""
        logger.info(f"Processing lecture: {lecture.title} (ID: {lecture.id})")
        
        try:
            # Step 1: Transcribe audio
            if not self.speech_to_text.is_available():
                logger.warning("Speech-to-text service not available")
                return
                
            logger.info(f"Transcribing audio for lecture: {lecture.title}")
            transcript = self.speech_to_text.transcribe_audio(lecture.audio_url)
            
            if not transcript:
                logger.error(f"Failed to transcribe audio for lecture: {lecture.title}")
                return
                
            logger.info(f"Transcription completed for lecture: {lecture.title}")
            
            # Step 2: Generate summary using Gemini
            if not self.gemini_service.is_available():
                logger.warning("Gemini service not available")
                return
                
            logger.info(f"Generating summary for lecture: {lecture.title}")
            summary = self.gemini_service.generate_summary(transcript)
            
            if not summary:
                logger.error(f"Failed to generate summary for lecture: {lecture.title}")
                return
                
            logger.info(f"Summary generated for lecture: {lecture.title}")
            
            # Step 3: Extract key points
            logger.info(f"Extracting key points for lecture: {lecture.title}")
            key_points = self.gemini_service.extract_key_points(transcript)
            
            # Step 4: Extract tasks
            logger.info(f"Extracting tasks for lecture: {lecture.title}")
            tasks_data = self.gemini_service.extract_tasks(transcript)
            
            # Update lecture with processed data
            lecture.transcript = transcript
            lecture.summary = summary
            lecture.key_points = ', '.join(key_points) if key_points else None
            lecture.is_processed = True
            lecture.updated_at = datetime.utcnow()
            
            # Create tasks from extracted data
            created_tasks = []
            if tasks_data:
                # Get all students for this teacher's lectures
                from models import User
                students = User.query.filter(User.role == 'student').all()
                
                for task_data in tasks_data:
                    # Create a task for each student
                    for student in students:
                        task = Task(
                            title=task_data.get('title', 'Extracted Task'),
                            description=task_data.get('description', ''),
                            lecture_id=lecture.id,
                            assigned_to_id=student.id,  # Assign to student
                            priority=TaskPriority(task_data.get('priority', 'medium')),
                            due_date=task_data.get('due_date'),
                            is_ai_generated=True
                        )
                        db.session.add(task)
                        created_tasks.append(task)
            
            db.session.commit()
            
            logger.info(f"Successfully processed lecture: {lecture.title}")
            logger.info(f"Created {len(created_tasks)} tasks from lecture")
            
        except Exception as e:
            logger.error(f"Error processing lecture {lecture.id}: {str(e)}")
            db.session.rollback()
            raise
            
    def process_lecture_immediately(self, lecture_id: str) -> dict:
        """Process a specific lecture immediately"""
        try:
            lecture = Lecture.query.get(lecture_id)
            if not lecture:
                return {'success': False, 'message': 'Lecture not found'}
                
            if lecture.is_processed:
                return {'success': True, 'message': 'Lecture already processed'}
                
            if not lecture.audio_url:
                return {'success': False, 'message': 'No audio file found'}
                
            self._process_lecture(lecture)
            
            return {
                'success': True, 
                'message': 'Lecture processed successfully',
                'lecture_id': lecture_id
            }
            
        except Exception as e:
            logger.error(f"Error processing lecture immediately: {str(e)}")
            return {'success': False, 'message': f'Processing failed: {str(e)}'}
            
    def get_processing_status(self) -> dict:
        """Get the current processing status"""
        try:
            total_lectures = Lecture.query.count()
            processed_lectures = Lecture.query.filter(Lecture.is_processed == True).count()
            unprocessed_lectures = Lecture.query.filter(
                Lecture.audio_url.isnot(None),
                Lecture.is_processed == False
            ).count()
            
            return {
                'is_running': self.is_running,
                'total_lectures': total_lectures,
                'processed_lectures': processed_lectures,
                'unprocessed_lectures': unprocessed_lectures,
                'processing_interval': self.processing_interval
            }
            
        except Exception as e:
            logger.error(f"Error getting processing status: {str(e)}")
            return {'error': str(e)}

# Global instance
background_processor = BackgroundProcessor()
