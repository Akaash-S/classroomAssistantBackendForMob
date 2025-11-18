#!/usr/bin/env python3
"""Quick S3 Test - One command to test everything"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Quick S3 Test\n")

# Check environment
print("1. Checking environment variables...")
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
aws_bucket = os.getenv('AWS_S3_BUCKET')

if not all([aws_key, aws_secret, aws_region, aws_bucket]):
    print("❌ AWS credentials not configured!")
    print("\nAdd to backend/.env:")
    print("AWS_ACCESS_KEY_ID=your_key")
    print("AWS_SECRET_ACCESS_KEY=your_secret")
    print("AWS_REGION=ap-south-1")
    print("AWS_S3_BUCKET=classroom-assistant-audio")
    exit(1)

print(f"✅ AWS Key: {aws_key[:10]}...")
print(f"✅ Region: {aws_region}")
print(f"✅ Bucket: {aws_bucket}")

# Test S3
print("\n2. Testing S3 connection...")
try:
    from services.s3_storage import S3StorageService
    s3 = S3StorageService()
    
    if not s3.is_available():
        print("❌ S3 not available!")
        print("Creating bucket...")
        if s3.create_bucket():
            print("✅ Bucket created!")
        else:
            print("❌ Failed to create bucket")
            exit(1)
    else:
        print("✅ S3 is available!")
    
    # Test upload
    print("\n3. Testing file upload...")
    test_data = b"Test from Classroom Assistant"
    url = s3.upload_audio("quick_test.txt", test_data)
    
    if url:
        print(f"✅ Upload successful!")
        print(f"📎 URL: {url}")
        print("\n✅ ALL TESTS PASSED! S3 is working correctly.")
    else:
        print("❌ Upload failed!")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nRun full test: python test_s3_endpoint.py")
    exit(1)
