import requests
import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SpeechToTextService:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.rapidapi_host = os.getenv('RAPIDAPI_HOST', 'speech-to-text-ai.p.rapidapi.com')
        self.base_url = f"https://{self.rapidapi_host}"
        
        # API-specific configuration for the specific service
        self.api_endpoint = os.getenv('RAPIDAPI_ENDPOINT', '/transcribe')
        self.language_value = os.getenv('RAPIDAPI_LANG_VALUE', 'en')
        
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
            
            logger.info(f"Transcribing audio URL: {audio_url}")
            
            # Prepare headers for the specific API format
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.rapidapi_host,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Use query parameters as shown in the provided code
            import urllib.parse
            encoded_url = urllib.parse.quote(audio_url, safe='')
            
            # Build the endpoint with query parameters
            endpoint = f"/transcribe?url={encoded_url}&lang={self.language_value}&task=transcribe"
            
            logger.info(f"Making request to: {self.base_url}{endpoint}")
            logger.info(f"Request headers: {headers}")
            
            # Make API request using the exact format from the provided code
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                data="",  # Empty payload as in the provided code
                timeout=60
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response text: {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # Try different possible response fields
                    transcript = (result.get('transcript', '') or 
                                result.get('text', '') or 
                                result.get('result', '') or
                                result.get('transcription', '') or
                                result.get('data', {}).get('text', '') or
                                str(result))
                    
                    if transcript and len(transcript.strip()) > 0:
                        logger.info(f"Transcription successful, length: {len(transcript)}")
                        return transcript.strip()
                    else:
                        logger.warning(f"Empty transcript received: {result}")
                        return None
                        
                except Exception as json_error:
                    logger.error(f"Failed to parse JSON response: {json_error}")
                    logger.error(f"Raw response: {response.text}")
                    return None
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
