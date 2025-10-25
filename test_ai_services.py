#!/usr/bin/env python3
"""
Test script for AI services (Speech-to-Text and Gemini)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.speech_to_text import SpeechToTextService
from services.gemini_service import GeminiService

def test_speech_to_text():
    """Test the Speech-to-Text service"""
    print("Testing Speech-to-Text Service...")
    
    # Check environment variables
    print(f"RAPIDAPI_KEY: {os.getenv('RAPIDAPI_KEY')[:20] + '...' if os.getenv('RAPIDAPI_KEY') else 'None'}")
    print(f"RAPIDAPI_HOST: {os.getenv('RAPIDAPI_HOST')}")
    
    # Initialize service
    service = SpeechToTextService()
    
    print(f"Service Available: {service.is_available()}")
    
    if service.is_available():
        print("Testing transcription with sample audio URL...")
        # Test with a sample audio URL (this will likely fail but will show the error)
        test_url = "https://example.com/test-audio.mp3"
        transcript = service.transcribe_audio(test_url)
        
        if transcript:
            print(f"Transcription SUCCESS: {transcript[:100]}...")
        else:
            print("Transcription FAILED (expected for test URL)")
    else:
        print("Speech-to-Text service is not available")

def test_gemini_service():
    """Test the Gemini service"""
    print("\nTesting Gemini Service...")
    
    # Check environment variables
    print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20] + '...' if os.getenv('GEMINI_API_KEY') else 'None'}")
    
    # Initialize service
    service = GeminiService()
    
    print(f"Service Available: {service.is_available()}")
    
    if service.is_available():
        print("Testing text summarization...")
        test_text = "This is a test text for summarization. It contains multiple sentences to demonstrate the summarization capabilities of the Gemini AI service."
        summary = service.generate_summary(test_text)
        
        if summary:
            print(f"Summarization SUCCESS: {summary[:100]}...")
        else:
            print("Summarization FAILED")
    else:
        print("Gemini service is not available")

def main():
    """Run all AI service tests"""
    print("AI SERVICES TEST")
    print("="*50)
    
    test_speech_to_text()
    test_gemini_service()
    
    print("\n" + "="*50)
    print("AI SERVICES TEST COMPLETED")

if __name__ == "__main__":
    main()
