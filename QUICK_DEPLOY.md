# 🚀 Quick Deploy to Render - 5 Minutes

## Step 1: Push Code (30 seconds)
```bash
git add .
git commit -m "Fix Render 502 error - ready for deployment"
git push origin main
```

## Step 2: Create Database (2 minutes)
1. Go to https://dashboard.render.com
2. Click **New +** → **PostgreSQL**
3. Settings:
   - Name: `classroom-assistant-db`
   - Database: `classroom_assistant`
   - Region: Oregon
   - Plan: Starter ($7) or Free
4. Click **Create Database**
5. **Copy Internal Database URL** (starts with `postgres://`)

## Step 3: Create Web Service (2 minutes)
1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Settings:
   - Name: `classroom-assistant-backend`
   - Region: Oregon
   - Branch: `main`
   - Root Directory: `backend`
   - Environment: **Docker**
   - Plan: Starter ($7) or Free

## Step 4: Environment Variables (1 minute)
Click **Advanced** → Add these variables:

```env
FLASK_ENV=production
FLASK_DEBUG=0
PYTHONUNBUFFERED=1
SECRET_KEY=your-secret-key-min-32-characters-long
DATABASE_URL=<paste-internal-database-url-here>
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
CORS_ORIGINS=*
```

**Optional** (if using AWS S3):
```env
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket
```

## Step 5: Deploy (5-10 minutes)
1. Click **Create Web Service**
2. Wait for deployment
3. Watch logs for:
   ```
   ✓ Database connection successful!
   ✓ Database tables created successfully!
   Starting Gunicorn server...
   ```

## Step 6: Verify (30 seconds)
```bash
# Replace with your service URL
curl https://your-service.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "port": "10000",
  "environment": "production"
}
```

## ✅ Success!
Your backend is now live at:
```
https://your-service-name.onrender.com
```

## 🐛 If You Get 502 Error

**Check Logs:**
- Render Dashboard → Your Service → Logs

**Common Fixes:**
1. Verify DATABASE_URL is set correctly
2. Check all environment variables are present
3. Ensure SECRET_KEY is at least 32 characters
4. Wait 2-3 minutes for full startup

**Still Issues?**
See `RENDER_DEPLOYMENT.md` for detailed troubleshooting.

---

**Total Time:** ~5-10 minutes
**Cost:** $0 (Free) or $14/month (Starter)
**Status:** ✅ Ready to Deploy
