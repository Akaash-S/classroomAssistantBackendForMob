# Docker S3 Configuration Fix

## Problem
"Failed to save lecture" error when uploading audio files in Docker deployment.

## Root Cause
The `docker-compose.yml` file was **missing AWS S3 environment variables**, so the backend container couldn't access S3 storage even though:
- AWS credentials were in `.env` file
- S3 test script passed when run locally
- Backend code was correctly configured

## Solution Applied

### 1. Updated `docker-compose.yml`
Added missing AWS S3 environment variables to the backend service:

```yaml
environment:
  # AWS S3 Storage
  AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
  AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
  AWS_REGION: ${AWS_REGION}
  AWS_S3_BUCKET: ${AWS_S3_BUCKET}
  
  # RapidAPI (Speech-to-Text)
  RAPIDAPI_KEY: ${RAPIDAPI_KEY}
  RAPIDAPI_HOST: ${RAPIDAPI_HOST}
  RAPIDAPI_ENDPOINT: ${RAPIDAPI_ENDPOINT}
  RAPIDAPI_LANG_VALUE: ${RAPIDAPI_LANG_VALUE}
```

### 2. Removed Unused Dependencies
- Removed `google-credentials.json` volume mount (not used)
- Removed Firebase and Google Cloud environment variables (not used)
- Cleaned up docker-compose to only include active services

### 3. Updated Dockerfile
Added comment clarifying that AWS credentials are passed via environment variables, not files.

## How to Apply the Fix

### Option 1: Quick Restart (Recommended)
```powershell
# Windows PowerShell
cd backend
.\restart-docker.ps1
```

```bash
# Linux/Mac
cd backend
chmod +x restart-docker.sh
./restart-docker.sh
```

### Option 2: Manual Restart
```bash
cd backend

# Stop containers
docker-compose down

# Start with updated configuration
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### Option 3: Full Rebuild (if Dockerfile changed)
```bash
cd backend
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f backend
```

## Verification Steps

### 1. Check Container Environment Variables
```bash
docker-compose exec backend env | grep AWS
```

Expected output:
```
AWS_ACCESS_KEY_ID=AKIAUT7VVE...
AWS_SECRET_ACCESS_KEY=oAjKWaGQUd...
AWS_REGION=ap-south-1
AWS_S3_BUCKET=classroom-assistant-audio
```

### 2. Test S3 from Inside Container
```bash
docker-compose exec backend python test_s3_endpoint.py
```

Expected: All 8 tests should pass.

### 3. Test Lecture Upload
1. Open your frontend application
2. Create a new lecture
3. Upload an audio file
4. Verify no "Failed to save lecture" error
5. Check backend logs: `docker-compose logs backend | grep -i "upload\|s3"`

## What This Fixes

✅ Audio file uploads for lectures
✅ Profile image uploads
✅ Chat document uploads
✅ All S3 storage operations in Docker

## Files Modified

1. `backend/docker-compose.yml` - Added AWS environment variables
2. `backend/Dockerfile` - Added clarifying comments
3. `backend/DOCKER_S3_DEPLOYMENT.md` - New deployment guide
4. `backend/restart-docker.ps1` - Windows restart script
5. `backend/restart-docker.sh` - Linux/Mac restart script
6. `backend/DOCKER_FIX_SUMMARY.md` - This file

## Why This Happened

Docker containers are **isolated environments**. Even though:
- Your `.env` file had AWS credentials
- Local Python scripts could access S3
- The backend code was correct

The Docker container couldn't see those credentials because `docker-compose.yml` wasn't configured to pass them through.

## Prevention

Always ensure `docker-compose.yml` includes ALL required environment variables from `.env`:

```yaml
environment:
  VARIABLE_NAME: ${VARIABLE_NAME}
```

This tells Docker Compose to read `VARIABLE_NAME` from `.env` and pass it to the container.

## Additional Notes

### For Render Deployment
Render doesn't use `docker-compose.yml`. Instead:
1. Set environment variables in Render dashboard
2. Render reads `Dockerfile` directly
3. Environment variables are automatically available in container

### For EC2 Deployment
Use docker-compose or set environment variables in:
- `.env` file (for docker-compose)
- Systemd service file (for direct Docker run)
- AWS Systems Manager Parameter Store (for production)

## Support

If issues persist after applying this fix:

1. **Check logs**: `docker-compose logs backend`
2. **Verify env vars**: `docker-compose exec backend env | grep AWS`
3. **Test S3**: `docker-compose exec backend python test_s3_endpoint.py`
4. **Check IAM permissions**: Ensure user has `AmazonS3FullAccess`
5. **Verify bucket exists**: Check AWS S3 console

## Success Indicators

After applying the fix, you should see in logs:
```
INFO - S3 client initialized for bucket: classroom-assistant-audio
INFO - Uploading [filename] to S3 bucket classroom-assistant-audio
INFO - Audio file uploaded successfully: [filename] -> https://...
```

No more "Storage service not available" or "Failed to save lecture" errors!
