# S3 Storage Endpoint Test Guide

## Quick Start

### Run the Test

```bash
cd backend
python test_s3_endpoint.py
```

## What the Test Does

The test suite performs 8 comprehensive checks:

1. **✓ Environment Variables** - Verifies AWS credentials are set
2. **✓ S3 Client Initialization** - Tests boto3 client setup
3. **✓ S3 Service Availability** - Checks bucket access
4. **✓ Audio File Upload** - Tests lecture audio upload
5. **✓ Image File Upload** - Tests profile image upload
6. **✓ Document File Upload** - Tests chat document upload
7. **✓ File Listing** - Tests bucket file listing
8. **✓ Bucket Permissions** - Checks ACL, policy, and CORS

## Expected Output

### Success:
```
======================================================================
  AWS S3 Storage Endpoint Test Suite
  Classroom Assistant Backend
======================================================================

======================================================================
  1. Testing Environment Variables
======================================================================
✓ AWS_ACCESS_KEY_ID: AKIAUT7VVE...LCXM
✓ AWS_SECRET_ACCESS_KEY: 27kq8Rgll+...m9ru
✓ AWS_REGION: ap-south-1
✓ AWS_S3_BUCKET: classroom-assistant-audio

✓ All environment variables are set!

======================================================================
  2. Testing S3 Client Initialization
======================================================================
✓ S3 client initialized successfully
  Bucket: classroom-assistant-audio
  Region: ap-south-1

======================================================================
  3. Testing S3 Service Availability
======================================================================
✓ S3 service is available
  Bucket 'classroom-assistant-audio' is accessible

======================================================================
  4. Testing Audio File Upload
======================================================================
Uploading test file: test_audio_upload.txt
File size: 58 bytes
✓ Audio upload successful!
  URL: https://classroom-assistant-audio.s3.ap-south-1.amazonaws.com/audio/test_audio_upload.txt

======================================================================
  5. Testing Image File Upload
======================================================================
Uploading test image: test_profile_image.jpg
File size: 34 bytes
✓ Image upload successful!
  URL: https://classroom-assistant-audio.s3.ap-south-1.amazonaws.com/images/profiles/test_profile_image.jpg

======================================================================
  6. Testing Document File Upload
======================================================================
Uploading test document: test_document.pdf
Room ID: test-room-123
File size: 31 bytes
✓ Document upload successful!
  URL: https://classroom-assistant-audio.s3.ap-south-1.amazonaws.com/documents/test-room-123/20241118_123456_test_document.pdf

======================================================================
  7. Testing File Listing
======================================================================
Listing files in 'audio/' folder...
✓ Found 1 file(s) in audio/ folder

  Files:
    - audio/test_audio_upload.txt

======================================================================
  8. Testing Bucket Permissions
======================================================================
Checking bucket permissions...
✓ Can read bucket ACL
✓ Bucket has a policy set
✓ CORS is configured

======================================================================
  Test Summary
======================================================================

Tests Passed: 8/8

Detailed Results:
  ✓ PASS - Environment Variables
  ✓ PASS - S3 Client Initialization
  ✓ PASS - S3 Service Availability
  ✓ PASS - Audio File Upload
  ✓ PASS - Image File Upload
  ✓ PASS - Document File Upload
  ✓ PASS - File Listing
  ✓ PASS - Bucket Permissions

======================================================================
  ✓ ALL TESTS PASSED!
  Your S3 storage is configured correctly.
======================================================================
```

## Troubleshooting

### Error: "Environment variables not set"

**Fix:**
```bash
# Edit backend/.env and add:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
AWS_S3_BUCKET=classroom-assistant-audio
```

### Error: "S3 client initialization failed"

**Possible causes:**
1. Invalid AWS credentials
2. boto3 not installed

**Fix:**
```bash
# Install boto3
pip install boto3

# Verify credentials in .env file
cat backend/.env | grep AWS
```

### Error: "Bucket does not exist"

**Fix:**
The test will automatically try to create the bucket. If it fails:

1. Create bucket manually in AWS Console
2. Or run: `python setup_aws_s3.py`

### Error: "Access Denied"

**Possible causes:**
1. IAM user doesn't have S3 permissions
2. Bucket policy blocks access

**Fix:**
1. Go to AWS IAM Console
2. Attach `AmazonS3FullAccess` policy to your user
3. Or see `AWS_S3_SETUP_FIX.md` for detailed steps

### Error: "Upload failed"

**Check:**
1. Bucket exists
2. Credentials are correct
3. IAM user has write permissions
4. No bucket policy blocking uploads

**Fix:**
```bash
# Re-run setup
python setup_aws_s3.py

# Or manually check AWS Console
```

## Quick Fixes

### Fix 1: Remove Quotes from .env

If your `.env` has quotes around values:
```env
# WRONG
AWS_ACCESS_KEY_ID='AKIA...'

# CORRECT
AWS_ACCESS_KEY_ID=AKIA...
```

### Fix 2: Restart Backend

After changing `.env`:
```bash
# Docker
docker-compose restart backend

# Direct
# Stop and restart python app.py
```

### Fix 3: Verify Credentials

```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key:', os.getenv('AWS_ACCESS_KEY_ID')[:10])"
```

## Integration Test

After S3 tests pass, test the full upload flow:

```bash
# Test lecture upload endpoint
curl -X POST http://localhost:5000/api/lectures \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Lecture",
    "subject": "Testing",
    "teacher_id": "your-teacher-id"
  }'
```

## Next Steps

1. ✅ Run `python test_s3_endpoint.py`
2. ✅ Fix any errors shown
3. ✅ Restart backend
4. ✅ Try uploading a lecture from the app
5. ✅ Check if files appear in S3 bucket

## Files Reference

- `test_s3_endpoint.py` - This test script
- `setup_aws_s3.py` - Interactive setup script
- `AWS_S3_SETUP_FIX.md` - Detailed setup guide
- `FIX_LECTURE_UPLOAD_ERROR.md` - Quick fix guide
- `.env` - Environment configuration

## Support

If tests still fail after trying fixes:

1. Check `AWS_S3_SETUP_FIX.md` for detailed troubleshooting
2. Verify AWS credentials in AWS Console
3. Check IAM user permissions
4. Verify bucket exists and is accessible
5. Check backend logs for detailed errors

---

**Remember:** After any `.env` changes, always restart the backend!
