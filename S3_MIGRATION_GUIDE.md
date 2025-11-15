# AWS S3 Migration Guide

This guide explains the migration from Supabase storage to AWS S3 for audio file storage.

## What Changed

### Backend Changes
- **Storage Service**: Replaced `SupabaseStorageService` with `S3StorageService`
- **Dependencies**: Replaced `supabase` package with `boto3` (AWS SDK)
- **Configuration**: Updated environment variables from Supabase to AWS S3
- **Auto-creation**: S3 bucket is automatically created if it doesn't exist

### Files Modified
1. `backend/requirements.txt` - Updated dependencies
2. `backend/.env` - Updated configuration variables
3. `backend/config.py` - Updated config class
4. `backend/services/s3_storage.py` - New S3 storage service
5. `backend/routes/lectures.py` - Updated to use S3 service
6. `backend/services/background_processor.py` - Updated import

### Files Added
1. `backend/services/s3_storage.py` - S3 storage implementation
2. `backend/setup_s3_bucket.py` - Bucket setup script
3. `backend/test_s3_storage.py` - S3 testing script
4. `backend/test_all_endpoints.py` - Comprehensive endpoint tests

## Setup Instructions

### Step 1: Get AWS Credentials

1. **Create AWS Account** (if you don't have one)
   - Go to https://aws.amazon.com/
   - Sign up for a free account

2. **Create IAM User**
   - Go to AWS Console → IAM → Users
   - Click "Add users"
   - Username: `classroom-assistant-app`
   - Access type: ✓ Programmatic access
   - Click "Next: Permissions"

3. **Set Permissions**
   - Click "Attach existing policies directly"
   - Search and select: `AmazonS3FullAccess`
   - Click "Next" → "Create user"

4. **Save Credentials**
   - Copy the **Access Key ID**
   - Copy the **Secret Access Key**
   - ⚠️ Save these securely - you won't see the secret key again!

### Step 2: Update Environment Variables

Edit `backend/.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
AWS_REGION=us-east-1
AWS_S3_BUCKET=classroom-assistant-audio
```

**Region Options:**
- `us-east-1` - US East (N. Virginia) - Default
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland)
- `ap-southeast-1` - Asia Pacific (Singapore)
- See full list: https://docs.aws.amazon.com/general/latest/gr/s3.html

**Bucket Name:**
- Must be globally unique across all AWS accounts
- Use lowercase letters, numbers, and hyphens only
- If the default name is taken, try: `classroom-assistant-audio-yourname`

### Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Set Up S3 Bucket

Run the setup script:

```bash
python setup_s3_bucket.py
```

This script will:
- ✓ Verify your AWS credentials
- ✓ Create the S3 bucket
- ✓ Configure public read access
- ✓ Set up CORS for web access
- ✓ Test bucket access

### Step 5: Test the Setup

Run the S3 storage test:

```bash
python test_s3_storage.py
```

Run comprehensive endpoint tests:

```bash
python test_all_endpoints.py
```

## How It Works

### File Upload Flow

1. **Frontend** → Sends audio file to backend API
2. **Backend** → Receives file via `/lectures/{id}/upload-audio`
3. **S3 Service** → Uploads file to S3 bucket
4. **S3** → Returns public URL
5. **Backend** → Saves URL to database
6. **Frontend** → Receives URL and can access file

### File Storage Structure

```
classroom-assistant-audio/
├── audio/
│   ├── {lecture_id}_{uuid}.m4a
│   ├── {lecture_id}_{uuid}.mp3
│   └── ...
└── images/
    └── profiles/
        └── {user_id}_{uuid}.jpg
```

### Public URLs

Files are accessible via:
```
https://{bucket-name}.s3.{region}.amazonaws.com/audio/{filename}
```

Example:
```
https://classroom-assistant-audio.s3.us-east-1.amazonaws.com/audio/abc123_def456.m4a
```

## Features

### Automatic Bucket Creation
The S3 service automatically creates the bucket if it doesn't exist when:
- The service is initialized
- A file upload is attempted
- `is_available()` is called

### Public Access Configuration
Files are automatically configured for public read access:
- Bucket policy allows public GetObject
- Individual files have ACL='public-read'
- CORS enabled for web access

### Error Handling
The service handles common errors:
- Missing credentials
- Bucket doesn't exist → Auto-creates
- Access denied → Clear error message
- Network errors → Retry logic

## Troubleshooting

### Error: "Access Denied"
**Solution:** Check IAM user permissions
```bash
# Required permissions:
- s3:CreateBucket
- s3:PutObject
- s3:GetObject
- s3:DeleteObject
- s3:PutBucketPolicy
- s3:PutBucketCORS
- s3:DeletePublicAccessBlock
```

### Error: "Bucket name already taken"
**Solution:** Change bucket name in `.env`
```env
AWS_S3_BUCKET=classroom-assistant-audio-yourname
```

### Error: "Credentials not found"
**Solution:** Verify `.env` file has correct credentials
```bash
# Check if variables are set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('AWS_ACCESS_KEY_ID'))"
```

### Files not publicly accessible
**Solution:** Run setup script again
```bash
python setup_s3_bucket.py
```

## Cost Estimation

AWS S3 pricing (as of 2024):

**Storage:**
- First 50 TB: $0.023 per GB/month
- Example: 100 GB = ~$2.30/month

**Requests:**
- PUT requests: $0.005 per 1,000 requests
- GET requests: $0.0004 per 1,000 requests

**Data Transfer:**
- First 100 GB/month: FREE
- Next 10 TB: $0.09 per GB

**Example Monthly Cost:**
- 1,000 audio files (10 MB each) = 10 GB storage = $0.23
- 10,000 uploads = $0.05
- 100,000 downloads (within free tier) = $0
- **Total: ~$0.28/month**

**Free Tier (First 12 months):**
- 5 GB storage
- 20,000 GET requests
- 2,000 PUT requests
- 100 GB data transfer out

## Migration from Supabase

If you have existing files in Supabase:

1. **Download files from Supabase**
2. **Upload to S3** using the API or AWS CLI
3. **Update database** with new S3 URLs

Script for migration (if needed):
```python
# migration_script.py
from services.s3_storage import S3StorageService
import requests

s3_service = S3StorageService()

# Get all lectures with Supabase URLs
lectures = Lecture.query.filter(Lecture.audio_url.like('%supabase%')).all()

for lecture in lectures:
    # Download from Supabase
    response = requests.get(lecture.audio_url)
    file_content = response.content
    
    # Upload to S3
    filename = lecture.audio_url.split('/')[-1]
    new_url = s3_service.upload_audio(filename, file_content)
    
    # Update database
    lecture.audio_url = new_url
    db.session.commit()
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use IAM roles** in production (EC2, ECS, Lambda)
3. **Enable bucket versioning** for backup
4. **Set up lifecycle policies** to archive old files
5. **Monitor costs** with AWS Budgets
6. **Use CloudFront** for better performance (optional)

## Support

For issues or questions:
1. Check AWS S3 documentation: https://docs.aws.amazon.com/s3/
2. Review boto3 documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
3. Check application logs for detailed error messages
