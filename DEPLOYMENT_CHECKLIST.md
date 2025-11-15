# Render Deployment Checklist

Use this checklist to ensure a smooth deployment to Render.

## Pre-Deployment Checklist

### 1. AWS S3 Setup
- [ ] AWS account created
- [ ] IAM user created with S3 permissions
- [ ] Access Key ID and Secret Access Key saved
- [ ] S3 bucket created (or will auto-create)
- [ ] Tested locally: `python test_s3_storage.py`

### 2. API Keys
- [ ] RapidAPI key obtained (for transcription)
- [ ] Gemini API key obtained (for AI features)
- [ ] All keys tested locally

### 3. Database
- [ ] PostgreSQL database ready (Neon/Render/Supabase)
- [ ] Database connection string obtained
- [ ] Database tested locally

### 4. Code Repository
- [ ] Code pushed to GitHub
- [ ] Repository is public or Render has access
- [ ] All changes committed
- [ ] `.env` file NOT committed (in .gitignore)

### 5. Configuration Files
- [ ] `Dockerfile` updated and tested
- [ ] `render.yaml` configured (optional)
- [ ] `requirements.txt` up to date
- [ ] `.dockerignore` configured

## Deployment Steps

### Step 1: Prepare Environment Variables

Copy these values (you'll need them in Render):

```
DATABASE_URL=postgresql://...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
AWS_S3_BUCKET=classroom-assistant-audio
RAPIDAPI_KEY=...
GEMINI_API_KEY=...
SECRET_KEY=... (generate new for production)
CORS_ORIGINS=https://your-frontend.com
```

### Step 2: Create Render Service

- [ ] Go to [Render Dashboard](https://dashboard.render.com/)
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Select repository and branch

### Step 3: Configure Service

**Basic Settings:**
- [ ] Name: `classroom-assistant-backend`
- [ ] Region: Selected (closest to users)
- [ ] Branch: `main`
- [ ] Root Directory: `backend`
- [ ] Environment: `Docker`
- [ ] Dockerfile Path: `./Dockerfile`

**Instance Type:**
- [ ] Free (for testing) OR
- [ ] Starter $7/month (for production)

### Step 4: Add Environment Variables

Add all environment variables from Step 1:

- [ ] DATABASE_URL
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY
- [ ] AWS_REGION
- [ ] AWS_S3_BUCKET
- [ ] RAPIDAPI_KEY
- [ ] GEMINI_API_KEY
- [ ] SECRET_KEY
- [ ] CORS_ORIGINS
- [ ] FLASK_ENV=production
- [ ] FLASK_DEBUG=False

### Step 5: Deploy

- [ ] Click "Create Web Service"
- [ ] Wait for build to complete (5-10 minutes)
- [ ] Check logs for errors

## Post-Deployment Verification

### 1. Health Check
- [ ] Visit: `https://your-app.onrender.com/api/health`
- [ ] Response: `{"status": "healthy", ...}`

### 2. Check Logs
- [ ] No error messages in logs
- [ ] S3 client initialized successfully
- [ ] Database connected
- [ ] Gunicorn started

### 3. Test Endpoints

Test these endpoints:

- [ ] `GET /api/health` - Health check
- [ ] `POST /api/auth/register` - User registration
- [ ] `POST /api/auth/login` - User login
- [ ] `GET /api/lectures` - Get lectures
- [ ] `POST /api/lectures` - Create lecture
- [ ] `POST /api/lectures/{id}/upload-audio` - Upload audio

### 4. Test S3 Upload

- [ ] Upload audio file through API
- [ ] Verify file appears in S3 bucket
- [ ] Verify public URL is accessible
- [ ] Check file can be downloaded

### 5. Update Frontend

- [ ] Update API_BASE_URL in frontend
- [ ] Test frontend with deployed backend
- [ ] Verify CORS is working
- [ ] Test all features end-to-end

## Monitoring Setup

### 1. Render Monitoring
- [ ] Enable email notifications for failures
- [ ] Set up Slack/Discord webhooks (optional)
- [ ] Review metrics dashboard

### 2. AWS Monitoring
- [ ] Check S3 bucket metrics
- [ ] Set up billing alerts
- [ ] Monitor storage usage

### 3. Database Monitoring
- [ ] Check database connection pool
- [ ] Monitor query performance
- [ ] Set up backup schedule

## Troubleshooting Checklist

If deployment fails, check:

- [ ] All environment variables are set correctly
- [ ] DATABASE_URL is valid and accessible
- [ ] AWS credentials are correct
- [ ] S3 bucket exists or can be created
- [ ] Dockerfile builds successfully locally
- [ ] No syntax errors in code
- [ ] All dependencies in requirements.txt
- [ ] Port binding is dynamic (uses $PORT)

## Performance Optimization

After successful deployment:

- [ ] Monitor response times
- [ ] Check memory usage
- [ ] Optimize database queries if needed
- [ ] Consider CDN for S3 files
- [ ] Enable caching where appropriate
- [ ] Scale workers if needed

## Security Checklist

- [ ] All secrets in environment variables (not code)
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS properly configured
- [ ] Database uses SSL connection
- [ ] S3 bucket has proper permissions
- [ ] Rate limiting implemented (if needed)
- [ ] Input validation in place

## Backup & Recovery

- [ ] Database backups enabled
- [ ] S3 versioning enabled (optional)
- [ ] Environment variables documented
- [ ] Deployment process documented
- [ ] Rollback plan in place

## Cost Monitoring

- [ ] Render plan selected and understood
- [ ] AWS billing alerts set up
- [ ] Database costs understood
- [ ] Monthly budget established
- [ ] Usage monitored regularly

## Documentation

- [ ] Deployment URL documented
- [ ] Environment variables documented (securely)
- [ ] API endpoints documented
- [ ] Frontend updated with new URL
- [ ] Team notified of deployment

## Final Checks

- [ ] All tests passing
- [ ] No errors in logs
- [ ] Health check responding
- [ ] API endpoints working
- [ ] File uploads working
- [ ] Frontend connected
- [ ] CORS configured
- [ ] Performance acceptable
- [ ] Monitoring set up
- [ ] Documentation updated

---

## Quick Commands

### Test Locally Before Deploy
```bash
# Test S3
python test_s3_storage.py

# Test all endpoints
python test_all_endpoints.py

# Build Docker image locally
docker build -t classroom-assistant-backend .

# Run Docker container locally
docker run -p 5000:5000 --env-file .env classroom-assistant-backend
```

### Deploy to Render
```bash
# Windows
deploy_to_render.bat

# Linux/Mac
./deploy_to_render.sh

# Or manually
git add .
git commit -m "Deploy to Render"
git push origin main
```

### Monitor Deployment
```bash
# View logs (from Render dashboard)
# Or use Render CLI
render logs -s your-service-name
```

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **AWS S3 Docs**: https://docs.aws.amazon.com/s3/
- **Deployment Guide**: `RENDER_DEPLOYMENT_GUIDE.md`
- **Migration Guide**: `S3_MIGRATION_GUIDE.md`

---

**Deployment Date**: _____________

**Deployed By**: _____________

**Deployment URL**: _____________

**Status**: ⬜ In Progress | ⬜ Complete | ⬜ Failed

**Notes**:
_____________________________________________
_____________________________________________
_____________________________________________
