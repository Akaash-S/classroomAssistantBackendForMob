import requests
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.rapidapi_host = os.getenv('RAPIDAPI_HOST', 'speech-to-text-api.p.rapidapi.com')
        self.base_url = f"https://{self.rapidapi_host}"
        
    def is_available(self) -> bool:
        """Check if the service is available"""
        return bool(self.rapidapi_key)
    
    def transcribe_audio(self, audio_url: str) -> Optional[str]:
        """
        Transcribe audio file using RapidAPI Speech-to-Text service
        
        Args:
            audio_url: URL of the audio file to transcribe
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not self.rapidapi_key:
                logger.error("RapidAPI key not configured")
                return None
            
            # Prepare headers
            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.rapidapi_host,
                'Content-Type': 'application/json'
            }
            
            # Prepare payload - check API documentation for correct format
            payload = {
                'url': audio_url,
                'language': 'en-US'
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/transcribe",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get('transcript', '')
                logger.info(f"Transcription successful, length: {len(transcript)}")
                return transcript
            else:
                logger.error(f"Transcription failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during transcription: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {str(e)}")
            return None
    
    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe local audio file
        
        Args:
            file_path: Path to the local audio file
            
        Returns:
            Transcribed text or None if failed
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"Audio file not found: {file_path}")
                return None
            
            # For local files, you might need to upload to a temporary storage first
            # or use a different API endpoint that accepts file uploads
            logger.info(f"Transcribing local file: {file_path}")
            
            # This is a placeholder - implement based on your RapidAPI service
            # You might need to upload the file to Supabase first, then use the URL
            return None
            
        except Exception as e:
            logger.error(f"Error transcribing local file: {str(e)}")
            return None
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats"""
        return ['mp3', 'wav', 'm4a', 'flac', 'ogg']
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'it-IT', 'pt-BR', 'ja-JP', 'ko-KR', 'zh-CN']
