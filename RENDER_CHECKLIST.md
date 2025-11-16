# Render Deployment Checklist

## ✅ Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] All environment variables ready
- [ ] API keys obtained (Gemini, Groq)
- [ ] Render account created

## ✅ Database Setup

- [ ] PostgreSQL database created on Render
- [ ] Database name: `classroom_assistant`
- [ ] Internal Database URL copied
- [ ] Database is running (green status)

## ✅ Service Configuration

- [ ] Web service created
- [ ] Docker environment selected
- [ ] Root directory set to `backend`
- [ ] Health check path: `/api/health`
- [ ] Auto-deploy enabled

## ✅ Environment Variables Set

### Required
- [ ] `FLASK_ENV=production`
- [ ] `FLASK_DEBUG=0`
- [ ] `PYTHONUNBUFFERED=1`
- [ ] `SECRET_KEY` (min 32 chars)
- [ ] `DATABASE_URL` (from database)
- [ ] `GEMINI_API_KEY`
- [ ] `GROQ_API_KEY`
- [ ] `CORS_ORIGINS=*`

### Optional
- [ ] `AWS_ACCESS_KEY_ID`
- [ ] `AWS_SECRET_ACCESS_KEY`
- [ ] `AWS_REGION`
- [ ] `AWS_S3_BUCKET`

## ✅ Deployment Verification

- [ ] Service deployed successfully
- [ ] No errors in logs
- [ ] Database connection successful
- [ ] Tables created
- [ ] Gunicorn started

## ✅ Endpoint Testing

- [ ] Root endpoint: `curl https://your-service.onrender.com/`
- [ ] Health check: `curl https://your-service.onrender.com/api/health`
- [ ] Auth health: `curl https://your-service.onrender.com/api/auth/health`
- [ ] Database status shows "connected"

## ✅ Post-Deployment

- [ ] Update frontend API URL
- [ ] Test all API endpoints
- [ ] Set up monitoring
- [ ] Configure production CORS (if needed)
- [ ] Document service URL

## 🚨 Troubleshooting

If you get 502 error:

1. **Check Logs**
   - Go to Render dashboard → Logs
   - Look for error messages

2. **Verify PORT**
   - Ensure PORT env var is set
   - Check app binds to correct port

3. **Database Connection**
   - Verify DATABASE_URL is correct
   - Check database is running
   - Test connection in logs

4. **Environment Variables**
   - All required vars are set
   - No typos in variable names
   - SECRET_KEY is long enough

## 📝 Service URL

Once deployed, your service will be at:
```
https://classroom-assistant-backend.onrender.com
```

(Replace with your actual service name)

## 🎯 Success Criteria

✅ Service status: "Live"
✅ Health endpoint returns 200
✅ Database status: "connected"
✅ No errors in logs
✅ All API endpoints accessible

---

**Ready to deploy!** Follow the detailed guide in `RENDER_DEPLOYMENT.md`
