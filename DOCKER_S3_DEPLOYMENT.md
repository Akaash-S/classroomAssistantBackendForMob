# Docker Deployment with S3 Storage

## Overview
This guide explains how to deploy the Classroom Assistant backend using Docker with AWS S3 storage.

## Prerequisites
- Docker and Docker Compose installed
- AWS S3 bucket created (`classroom-assistant-audio`)
- AWS IAM user with S3 access credentials
- `.env` file configured with all required variables

## Environment Variables Required

The following environment variables must be set in your `.env` file:

### Database
```env
DATABASE_URL=postgresql://user:password@host/database
```

### AWS S3 Storage (CRITICAL for file uploads)
```env
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_REGION=ap-south-1
AWS_S3_BUCKET=classroom-assistant-audio
```

### API Keys
```env
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=speech-to-text-ai.p.rapidapi.com
RAPIDAPI_ENDPOINT=/transcribe
RAPIDAPI_LANG_VALUE=en

GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

### Flask Configuration
```env
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:8081
```

## Deployment Steps

### 1. Verify Environment Variables
```bash
# Test S3 connection before deploying
python test_s3_endpoint.py
```

All tests should pass before proceeding.

### 2. Build and Start Containers
```bash
# Build the Docker image
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 3. Verify Deployment
```bash
# Check container status
docker-compose ps

# Test health endpoint
curl http://localhost:5000/api/health

# Check S3 connectivity from container
docker-compose exec backend python test_s3_endpoint.py
```

## Troubleshooting

### Issue: "Failed to save lecture" or "Storage service not available"

**Cause**: AWS credentials not passed to Docker container

**Solution**:
1. Verify `.env` file contains all AWS variables
2. Restart containers to pick up new environment variables:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Issue: "Access Denied" when uploading to S3

**Cause**: IAM user lacks S3 permissions

**Solution**:
1. Verify IAM user has `AmazonS3FullAccess` policy
2. Check bucket name matches in `.env` and AWS console
3. Verify credentials are correct (no extra spaces)

### Issue: Container fails to start

**Cause**: Missing required environment variables

**Solution**:
1. Check logs: `docker-compose logs backend`
2. Verify all required variables in `.env`
3. Ensure no syntax errors in `.env` file

## Container Architecture

```
┌─────────────────────────────────────────┐
│         Nginx (Port 80/443)             │
│         Reverse Proxy                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Flask Backend (Port 5000)            │
│    - API Endpoints                      │
│    - File Upload Handler                │
│    - S3 Integration                     │
└──────────────┬──────────────────────────┘
               │
               ├──────────────┐
               ▼              ▼
    ┌──────────────┐  ┌──────────────┐
    │  Neon DB     │  │   AWS S3     │
    │  (External)  │  │   Storage    │
    └──────────────┘  └──────────────┘
```

## Production Deployment

For production deployment on Render or other platforms:

1. **Set Environment Variables** in platform dashboard
2. **Use Dockerfile** (not docker-compose)
3. **Configure Health Checks** at `/api/health`
4. **Enable Auto-Deploy** from Git repository

### Render Deployment
```bash
# Render will automatically:
# 1. Detect Dockerfile
# 2. Build the image
# 3. Run the container
# 4. Expose the PORT environment variable

# You only need to:
# 1. Add all environment variables in Render dashboard
# 2. Deploy from GitHub repository
```

## Monitoring

### Check S3 Upload Status
```bash
# View backend logs
docker-compose logs -f backend | grep -i "s3\|upload\|storage"

# Test S3 from inside container
docker-compose exec backend python test_s3_endpoint.py
```

### Check Container Health
```bash
# View health check status
docker inspect classroom-backend | grep -A 10 Health

# Manual health check
curl http://localhost:5000/api/health
```

## Updating Deployment

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verify
docker-compose logs -f backend
```

## Security Notes

1. **Never commit `.env` file** to version control
2. **Rotate AWS credentials** regularly
3. **Use IAM roles** instead of access keys when possible (EC2/ECS)
4. **Enable S3 bucket encryption** at rest
5. **Configure CORS** properly for your frontend domain
6. **Use HTTPS** in production (Nginx with SSL certificates)

## Support

If you encounter issues:
1. Check logs: `docker-compose logs backend`
2. Test S3: `python test_s3_endpoint.py`
3. Verify environment variables are loaded
4. Check AWS IAM permissions
5. Review `FINAL_S3_SOLUTION.md` for S3 setup details
