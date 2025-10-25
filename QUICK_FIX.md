# 🚨 QUICK FIX: Recording Upload Error

## **Problem**
```
ERROR Failed to save lecture: [Error: Failed to upload file to storage]
```

## **Root Cause**
The backend is missing required environment variables, specifically Supabase credentials for file storage.

## **Immediate Solution**

### Option 1: Quick Setup (Recommended)
```bash
# Navigate to backend directory
cd backend

# Run the interactive setup script
python setup_env.py
```

This script will guide you through setting up all required environment variables.

### Option 2: Manual Setup
```bash
# Copy the environment template
cp env.example .env

# Edit the .env file with your Supabase credentials
# (Use your preferred editor)
```

### Option 3: Set Environment Variables Directly
```bash
# Set environment variables (Windows PowerShell)
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_KEY="your-supabase-anon-key"
$env:SUPABASE_SERVICE_KEY="your-supabase-service-key"
$env:SECRET_KEY="your-secret-key"
$env:DATABASE_URL="sqlite:///instance/classroom_assistant.db"

# Start the backend
python app.py
```

## **Required Supabase Setup**

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Wait for setup to complete

2. **Get Credentials**:
   - Go to Settings → API
   - Copy Project URL and API keys

3. **Create Storage Bucket**:
   - Go to Storage → New Bucket
   - Name: `lectures`
   - Make it **public** ✅

## **Test the Fix**

After setting up environment variables:

```bash
# Test environment
python check_env.py

# Test Supabase connection
python test_supabase.py

# Start backend
python app.py
```

## **Expected Results**

✅ Environment check should show all variables as "OK"  
✅ Supabase test should show "All tests passed"  
✅ Recording should upload successfully to Supabase storage  
✅ Lecture should appear in the database with audio_url populated  

## **Still Having Issues?**

1. **Check backend logs** for detailed error messages
2. **Verify Supabase project** is active and accessible
3. **Ensure `lectures` bucket** exists and is public
4. **Test with the provided scripts** to isolate the issue

The recording functionality will work once the environment variables are properly configured!
