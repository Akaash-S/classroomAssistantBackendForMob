# Render Deployment Guide - AWS S3 Backend

Complete guide to deploy the Classroom Assistant backend on Render with AWS S3 storage.

## Prerequisites

Before deploying, ensure you have:

1. ✅ **GitHub Account** - Code must be in a GitHub repository
2. ✅ **Render Account** - Sign up at [render.com](https://render.com)
3. ✅ **AWS Account** - With S3 bucket configured
4. ✅ **API Keys** - RapidAPI and Gemini API keys
5. ✅ **Database** - PostgreSQL database (Neon, Supabase, or Render)

## Step 1: Prepare Your Repository

### 1.1 Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Add AWS S3 storage and Render deployment config"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/classroom-assistant.git

# Push to GitHub
git push -u origin main
```

### 1.2 Verify Files

Ensure these files are in your repository:
- ✅ `backend/Dockerfile`
- ✅ `backend/render.yaml`
- ✅ `backend/requirements.txt`
- ✅ `backend/app.py`
- ✅ `backend/services/s3_storage.py`

## Step 2: Set Up AWS S3 Bucket

### 2.1 Create S3 Bucket

Run the setup script locally first:

```bash
cd backend
python setup_s3_bucket.py
```

This ensures your S3 bucket is properly configured before deployment.

### 2.2 Verify S3 Configuration

```bash
python test_s3_storage.py
```

Make sure all tests pass before deploying.

## Step 3: Deploy on Render

### 3.1 Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your repository

### 3.2 Configure Service

**Basic Settings:**
- **Name**: `classroom-assistant-backend`
- **Region**: Choose closest to your users (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: `backend`
- **Environment**: `Docker`
- **Dockerfile Path**: `./Dockerfile`

**Instance Type:**
- **Free Tier**: Good for testing (sleeps after 15 min inactivity)
- **Starter ($7/month)**: Recommended for production (always on)

### 3.3 Configure Environment Variables

Click **"Advanced"** and add these environment variables:

#### Database Configuration
```
DATABASE_URL = your-postgresql-connection-string
```

**Get PostgreSQL Database:**
- **Option A**: Use Render PostgreSQL (recommended)
  - Create new PostgreSQL database on Render
  - Copy the Internal Database URL
- **Option B**: Use Neon (free tier)
  - Go to [neon.tech](https://neon.tech)
  - Create database and copy connection string
- **Option C**: Use Supabase PostgreSQL
  - Get connection string from Supabase dashboard

#### AWS S3 Configuration
```
AWS_ACCESS_KEY_ID = your-aws-access-key-id
AWS_SECRET_ACCESS_KEY = your-aws-secret-access-key
AWS_REGION = us-east-1
AWS_S3_BUCKET = classroom-assistant-audio
```

#### RapidAPI Configuration
```
RAPIDAPI_KEY = your-rapidapi-key
RAPIDAPI_HOST = speech-to-text-ai.p.rapidapi.com
RAPIDAPI_ENDPOINT = /transcribe
RAPIDAPI_LANG_VALUE = en
```

#### Gemini API Configuration
```
GEMINI_API_KEY = your-gemini-api-key
```

#### Flask Configuration
```
FLASK_ENV = production
FLASK_DEBUG = False
SECRET_KEY = [Auto-generate or use your own]
```

#### CORS Configuration
```
CORS_ORIGINS = http://localhost:3000,http://localhost:8081,https://your-frontend-domain.com
```

### 3.4 Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Build Docker image
   - Install dependencies
   - Start the application
3. Wait for deployment to complete (5-10 minutes)

## Step 4: Verify Deployment

### 4.1 Check Health Endpoint

Once deployed, visit:
```
https://your-app-name.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Classroom Assistant API is running",
  "timestamp": "2024-11-15T12:00:00Z"
}
```

### 4.2 Test S3 Storage

Check the logs to verify S3 connection:
```
S3 client initialized for bucket: classroom-assistant-audio
Bucket classroom-assistant-audio exists and is accessible
```

### 4.3 Test API Endpoints

Use the test script with your deployed URL:

```bash
# Update API_BASE_URL in test script
export API_BASE_URL=https://your-app-name.onrender.com/api

# Run tests
python test_all_endpoints.py
```

## Step 5: Update Frontend

Update your frontend to use the deployed backend URL:

### React Native (frontend_new/services/api-service.ts)

```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5000/api'
  : 'https://your-app-name.onrender.com/api';
```

## Render Configuration Options

### Auto-Deploy

Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
# Render automatically deploys
```

### Manual Deploy

From Render Dashboard:
1. Go to your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**

### Environment Variables

Update environment variables:
1. Go to service → **"Environment"**
2. Add/Edit variables
3. Click **"Save Changes"**
4. Service automatically redeploys

## Monitoring & Logs

### View Logs

1. Go to your service on Render
2. Click **"Logs"** tab
3. View real-time logs

### Common Log Messages

**Successful Startup:**
```
S3 client initialized for bucket: classroom-assistant-audio
✓ Bucket classroom-assistant-audio is ready for use
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5000
```

**S3 Upload:**
```
Uploading test_audio.m4a to S3 bucket classroom-assistant-audio
Audio file uploaded successfully: test_audio.m4a -> https://...
```

### Health Checks

Render automatically monitors your service:
- Health check every 30 seconds
- Endpoint: `/api/health`
- Restarts if unhealthy

## Troubleshooting

### Issue: Build Fails

**Error**: `requirements.txt not found`
**Solution**: Ensure Root Directory is set to `backend`

**Error**: `Dockerfile not found`
**Solution**: Check Dockerfile Path is `./Dockerfile`

### Issue: Service Crashes on Startup

**Check Logs for:**
```
Error: DATABASE_URL not set
```
**Solution**: Add DATABASE_URL environment variable

```
Error: AWS credentials not found
```
**Solution**: Add AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

### Issue: S3 Upload Fails

**Error**: `Access Denied to bucket`
**Solution**: 
1. Verify AWS credentials are correct
2. Check IAM user has S3 permissions
3. Verify bucket name matches

**Error**: `Bucket does not exist`
**Solution**: 
1. Run `python setup_s3_bucket.py` locally first
2. Or let the service auto-create it (check logs)

### Issue: CORS Errors

**Error**: `CORS policy blocked`
**Solution**: Update CORS_ORIGINS environment variable:
```
CORS_ORIGINS = https://your-frontend-domain.com,http://localhost:3000
```

### Issue: Database Connection Fails

**Error**: `could not connect to server`
**Solution**:
1. Verify DATABASE_URL is correct
2. Check database is running
3. Ensure SSL mode is set correctly

## Performance Optimization

### 1. Use Render PostgreSQL

For best performance, use Render's PostgreSQL:
- Same region as web service
- Internal network connection
- Faster queries

### 2. Enable Persistent Disk (Optional)

If you need local file caching:
1. Go to service → **"Settings"**
2. Add **"Disk"**
3. Mount path: `/app/cache`

### 3. Scale Workers

For high traffic, increase Gunicorn workers:

Update Dockerfile CMD:
```dockerfile
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 8 --timeout 120 ...
```

### 4. Use CDN for S3

For better performance, use CloudFront:
1. Create CloudFront distribution
2. Point to S3 bucket
3. Update URLs in responses

## Cost Estimation

### Render Costs

**Free Tier:**
- 750 hours/month
- Sleeps after 15 min inactivity
- Good for testing

**Starter Plan ($7/month):**
- Always on
- 512 MB RAM
- Recommended for production

**Standard Plan ($25/month):**
- 2 GB RAM
- Better performance
- For high traffic

### AWS S3 Costs

See `S3_MIGRATION_GUIDE.md` for detailed cost breakdown.

**Typical Monthly Cost:**
- Storage (10 GB): $0.23
- Requests: $0.05
- Transfer (within free tier): $0
- **Total: ~$0.28/month**

### Total Monthly Cost

**Development**: Free (Render Free + S3 Free Tier)
**Production**: ~$7.28/month (Render Starter + S3)

## Security Best Practices

### 1. Environment Variables

✅ **DO**: Store secrets in Render environment variables
❌ **DON'T**: Commit secrets to GitHub

### 2. Database Security

✅ Use SSL connections
✅ Use strong passwords
✅ Restrict database access

### 3. S3 Security

✅ Use IAM user with minimal permissions
✅ Enable bucket versioning
✅ Set up lifecycle policies

### 4. API Security

✅ Use HTTPS only
✅ Implement rate limiting
✅ Validate all inputs

## Backup & Recovery

### Database Backups

**Render PostgreSQL:**
- Automatic daily backups
- 7-day retention (free tier)
- 30-day retention (paid plans)

**Manual Backup:**
```bash
pg_dump $DATABASE_URL > backup.sql
```

### S3 Backups

Enable versioning:
```bash
aws s3api put-bucket-versioning \
  --bucket classroom-assistant-audio \
  --versioning-configuration Status=Enabled
```

## Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          python -m pytest tests/
      
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

## Support & Resources

- **Render Documentation**: https://render.com/docs
- **AWS S3 Documentation**: https://docs.aws.amazon.com/s3/
- **Application Logs**: Render Dashboard → Your Service → Logs
- **Status Page**: https://status.render.com/

## Quick Reference

### Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] S3 bucket created and tested
- [ ] Render account created
- [ ] Web service created on Render
- [ ] All environment variables configured
- [ ] Service deployed successfully
- [ ] Health check passing
- [ ] API endpoints tested
- [ ] Frontend updated with new URL
- [ ] CORS configured correctly

### Environment Variables Checklist

- [ ] DATABASE_URL
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY
- [ ] AWS_REGION
- [ ] AWS_S3_BUCKET
- [ ] RAPIDAPI_KEY
- [ ] GEMINI_API_KEY
- [ ] SECRET_KEY
- [ ] CORS_ORIGINS

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Test file uploads
- [ ] Test all API endpoints
- [ ] Update frontend configuration
- [ ] Set up monitoring/alerts
- [ ] Document deployment URL

---

**Deployment Status**: Ready for Production ✅

**Last Updated**: November 15, 2025
