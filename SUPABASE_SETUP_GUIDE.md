# Supabase Storage Setup Guide

## 🚨 **Issue Identified**
The recording upload is failing because the backend is missing required environment variables, specifically Supabase credentials.

## ✅ **Solution Steps**

### 1. **Set Up Supabase Project**

#### Create a Supabase Project:
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login to your account
3. Click "New Project"
4. Choose your organization
5. Enter project details:
   - **Name**: `classroom-assistant` (or any name you prefer)
   - **Database Password**: Choose a strong password
   - **Region**: Select the closest region to your users
6. Click "Create new project"
7. Wait for the project to be set up (2-3 minutes)

#### Get Your Supabase Credentials:
1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like: `https://abcdefghijklmnop.supabase.co`)
   - **anon public** key (starts with `eyJ...`)
   - **service_role** key (starts with `eyJ...`)

### 2. **Create Storage Bucket**

#### In Supabase Dashboard:
1. Go to **Storage** in the left sidebar
2. Click **"New bucket"**
3. Enter bucket details:
   - **Name**: `lectures`
   - **Public bucket**: ✅ **Check this box** (important!)
4. Click **"Create bucket"**

#### Set Bucket Policies:
1. Go to **Storage** → **Policies**
2. Click **"New Policy"** for the `lectures` bucket
3. Create a policy for **INSERT** operations:
   ```sql
   CREATE POLICY "Allow public uploads" ON storage.objects
   FOR INSERT WITH CHECK (bucket_id = 'lectures');
   ```
4. Create a policy for **SELECT** operations:
   ```sql
   CREATE POLICY "Allow public downloads" ON storage.objects
   FOR SELECT USING (bucket_id = 'lectures');
   ```

### 3. **Configure Backend Environment**

#### Create .env file:
```bash
# Copy the example file
cp backend/env.example backend/.env
```

#### Edit backend/.env with your values:
```env
# Database Configuration
DATABASE_URL=sqlite:///instance/classroom_assistant.db

# Flask Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
FLASK_ENV=development

# Supabase Configuration (REQUIRED for file storage)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
SUPABASE_SERVICE_KEY=your-supabase-service-role-key-here

# AI Services (Optional - for transcript generation)
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. **Test the Configuration**

#### Run the environment check:
```bash
python backend/check_env.py
```

#### Run the Supabase test:
```bash
python backend/test_supabase.py
```

### 5. **Start the Backend**

#### Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

#### Start the server:
```bash
python app.py
```

## 🔧 **Troubleshooting**

### Issue: "Storage service not available"
**Solution**: Check that SUPABASE_URL and SUPABASE_KEY are set correctly

### Issue: "Failed to upload file to storage"
**Solutions**:
1. Verify the `lectures` bucket exists and is public
2. Check that bucket policies allow uploads
3. Ensure SUPABASE_SERVICE_KEY is set for admin operations

### Issue: "Bucket does not exist"
**Solution**: The test script will try to create the bucket automatically, or create it manually in the Supabase dashboard

### Issue: "Permission denied"
**Solution**: Check that your Supabase service role key has the correct permissions

## 📋 **Required Environment Variables**

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ Yes | Your Supabase project URL |
| `SUPABASE_KEY` | ✅ Yes | Your Supabase anon key |
| `SUPABASE_SERVICE_KEY` | ⚠️ Recommended | Service role key for admin operations |
| `DATABASE_URL` | ✅ Yes | Database connection string |
| `SECRET_KEY` | ✅ Yes | Flask secret key |
| `GEMINI_API_KEY` | ❌ Optional | For AI transcript generation |

## 🎯 **Quick Setup Commands**

```bash
# 1. Copy environment template
cp backend/env.example backend/.env

# 2. Edit the .env file with your Supabase credentials
# (Use your preferred editor: nano, vim, code, etc.)

# 3. Test configuration
python backend/check_env.py
python backend/test_supabase.py

# 4. Start backend
cd backend
python app.py
```

## ✅ **Verification Steps**

1. **Environment Check**: All required variables should show "OK"
2. **Supabase Test**: Should show "All tests passed"
3. **Recording Test**: Try recording a lecture and check console logs
4. **Storage Check**: Verify file appears in Supabase Storage → lectures bucket

## 🆘 **Need Help?**

If you're still having issues:
1. Check the backend logs for detailed error messages
2. Verify your Supabase project is active
3. Ensure the `lectures` bucket exists and is public
4. Test with the provided test scripts

The recording functionality will work once these environment variables are properly configured!
