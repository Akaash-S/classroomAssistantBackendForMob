#!/usr/bin/env python3
"""
Complete Lecture Workflow Test
Tests the entire flow: Create Lecture -> Upload Audio -> Process with AI
"""

import requests
import json
import time
import os
from io import BytesIO

BASE_URL = "http://localhost:5000"

def create_test_audio_file():
    """Create a small test audio file (simulated)"""
    # Create a minimal MP3 header for testing
    # This is a very basic MP3 file header that should be recognized as valid
    mp3_header = b'\xff\xfb\x90\x00'  # MP3 sync word + header
    test_content = mp3_header + b'This is a simulated audio file for testing purposes.' * 100
    return BytesIO(test_content)

def test_complete_lecture_workflow():
    """Test the complete lecture workflow"""
    print("COMPLETE LECTURE WORKFLOW TEST")
    print("="*60)
    
    # Step 1: Create a test teacher user first
    print("\nStep 1: Creating test teacher user...")
    teacher_data = {
        "firebase_uid": "test_teacher_123",
        "email": "teacher@test.com",
        "name": "Test Teacher",
        "role": "teacher",
        "department": "Computer Science"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=teacher_data)
        if response.status_code in [200, 201]:
            print("SUCCESS: Test teacher created successfully")
            teacher_id = response.json().get('user', {}).get('id')
        else:
            print(f"WARNING: Teacher creation failed: {response.text}")
            # Try to get existing teacher by Firebase UID
            try:
                get_response = requests.get(f"{BASE_URL}/api/auth/user/firebase/{teacher_data['firebase_uid']}")
                if get_response.status_code == 200:
                    teacher_id = get_response.json().get('user', {}).get('id')
                    print(f"SUCCESS: Found existing teacher with ID: {teacher_id}")
                else:
                    teacher_id = "test_teacher_123"
            except:
                teacher_id = "test_teacher_123"
    except Exception as e:
        print(f"WARNING: Teacher creation error: {str(e)}")
        teacher_id = "test_teacher_123"
    
    # Step 2: Create a new lecture
    print(f"\nStep 2: Creating new lecture...")
    lecture_data = {
        "title": "Test Lecture - AI and Machine Learning",
        "subject": "Computer Science",
        "teacher_id": teacher_id,
        "tags": ["AI", "Machine Learning", "Test"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/lectures/", json=lecture_data)
        if response.status_code == 201:
            lecture = response.json().get('lecture')
            lecture_id = lecture.get('id')
            print(f"SUCCESS: Lecture created successfully: {lecture.get('title')}")
            print(f"   Lecture ID: {lecture_id}")
        else:
            print(f"FAILED: Lecture creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Lecture creation error: {str(e)}")
        return False
    
    # Step 3: Upload audio file (simulated)
    print(f"\nStep 3: Uploading audio file...")
    try:
        # Create a test file
        test_file = create_test_audio_file()
        
        files = {
            'audio_file': ('test_audio.mp3', test_file, 'audio/mpeg')
        }
        
        data = {
            'audio_duration': '120'  # 2 minutes
        }
        
        response = requests.post(
            f"{BASE_URL}/api/lectures/{lecture_id}/upload-audio",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Audio uploaded successfully")
            print(f"   Audio URL: {result.get('audio_url', 'N/A')}")
        else:
            print(f"FAILED: Audio upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Audio upload error: {str(e)}")
        return False
    
    # Step 4: Process lecture with AI
    print(f"\nStep 4: Processing lecture with AI...")
    try:
        response = requests.post(f"{BASE_URL}/api/lectures/{lecture_id}/process")
        
        if response.status_code == 200:
            result = response.json()
            processing_results = result.get('processing_results', {})
            
            print(f"SUCCESS: Lecture processing completed")
            print(f"   Transcript generated: {processing_results.get('transcript_generated', False)}")
            print(f"   Summary generated: {processing_results.get('summary_generated', False)}")
            print(f"   Key points generated: {processing_results.get('key_points_generated', False)}")
            
            # Show the processed lecture data
            lecture_data = result.get('lecture', {})
            if lecture_data.get('transcript'):
                print(f"   Transcript length: {len(lecture_data['transcript'])} characters")
            if lecture_data.get('summary'):
                print(f"   Summary length: {len(lecture_data['summary'])} characters")
            if lecture_data.get('key_points'):
                print(f"   Key points length: {len(lecture_data['key_points'])} characters")
        else:
            print(f"FAILED: Lecture processing failed: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Lecture processing error: {str(e)}")
        return False
    
    # Step 5: Verify final lecture data
    print(f"\nStep 5: Verifying final lecture data...")
    try:
        response = requests.get(f"{BASE_URL}/api/lectures/{lecture_id}")
        
        if response.status_code == 200:
            lecture = response.json().get('lecture')
            print(f"SUCCESS: Final lecture verification successful")
            print(f"   Title: {lecture.get('title')}")
            print(f"   Audio URL: {'Present' if lecture.get('audio_url') else 'Missing'}")
            print(f"   Transcript: {'Present' if lecture.get('transcript') else 'Missing'}")
            print(f"   Summary: {'Present' if lecture.get('summary') else 'Missing'}")
            print(f"   Key Points: {'Present' if lecture.get('key_points') else 'Missing'}")
            print(f"   Processed: {'Yes' if lecture.get('is_processed') else 'No'}")
        else:
            print(f"FAILED: Lecture verification failed: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: Lecture verification error: {str(e)}")
        return False
    
    print(f"\n{'='*60}")
    print("COMPLETE LECTURE WORKFLOW TEST PASSED!")
    print(f"{'='*60}")
    return True

def main():
    """Run the complete workflow test"""
    print("Starting Complete Lecture Workflow Test...")
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    success = test_complete_lecture_workflow()
    
    if success:
        print("\nSUCCESS: All tests passed! The complete lecture workflow is working.")
    else:
        print("\nFAILED: Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
