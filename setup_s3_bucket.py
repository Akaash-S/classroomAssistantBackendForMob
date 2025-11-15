#!/usr/bin/env python3
"""
Script to set up AWS S3 bucket for the classroom assistant application
This script will:
1. Verify AWS credentials
2. Create the S3 bucket if it doesn't exist
3. Configure bucket for public read access
4. Set up CORS for web access
"""

import os
import sys
import logging
from dotenv import load_dotenv
from services.s3_storage import S3StorageService

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def verify_credentials():
    """Verify AWS credentials are set"""
    print_header("Step 1: Verifying AWS Credentials")
    
    required_vars = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
        'AWS_S3_BUCKET': os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')
    }
    
    missing = []
    for var, value in required_vars.items():
        if not value:
            missing.append(var)
            logger.error(f"✗ {var}: Not set")
        else:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                display = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            else:
                display = value
            logger.info(f"✓ {var}: {display}")
    
    if missing:
        logger.error(f"\n❌ Missing required variables: {', '.join(missing)}")
        logger.info("\nPlease add these to your backend/.env file:")
        logger.info("AWS_ACCESS_KEY_ID=your-access-key-id")
        logger.info("AWS_SECRET_ACCESS_KEY=your-secret-access-key")
        logger.info("AWS_REGION=us-east-1")
        logger.info("AWS_S3_BUCKET=classroom-assistant-audio")
        return False
    
    logger.info("\n✓ All credentials are set")
    return True


def create_bucket():
    """Create and configure S3 bucket"""
    print_header("Step 2: Creating S3 Bucket")
    
    try:
        storage_service = S3StorageService(auto_create_bucket=False)
        
        if not storage_service.s3_client:
            logger.error("❌ Failed to initialize S3 client")
            return False
        
        bucket_name = storage_service.bucket_name
        region = storage_service.aws_region
        
        logger.info(f"Bucket name: {bucket_name}")
        logger.info(f"Region: {region}")
        
        # Create bucket
        if storage_service.create_bucket():
            logger.info(f"\n✓ Bucket setup completed successfully!")
            return True
        else:
            logger.error(f"\n❌ Failed to create bucket")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error creating bucket: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


def test_bucket_access():
    """Test bucket access by uploading and deleting a test file"""
    print_header("Step 3: Testing Bucket Access")
    
    try:
        storage_service = S3StorageService(auto_create_bucket=False)
        
        # Create test file
        test_content = b"Test file for S3 bucket verification"
        test_filename = "test_file.txt"
        
        logger.info("Uploading test file...")
        
        # Upload test file
        s3_key = f"test/{test_filename}"
        storage_service.s3_client.put_object(
            Bucket=storage_service.bucket_name,
            Key=s3_key,
            Body=test_content,
            ContentType='text/plain',
            ACL='public-read'
        )
        
        # Generate URL
        public_url = f"https://{storage_service.bucket_name}.s3.{storage_service.aws_region}.amazonaws.com/{s3_key}"
        logger.info(f"✓ Test file uploaded: {public_url}")
        
        # Delete test file
        logger.info("Cleaning up test file...")
        storage_service.delete_file(s3_key)
        logger.info("✓ Test file deleted")
        
        logger.info("\n✓ Bucket access test passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Bucket access test failed: {str(e)}")
        return False


def print_summary():
    """Print setup summary"""
    print_header("Setup Complete!")
    
    bucket_name = os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"""
✓ AWS S3 bucket is ready for use!

Bucket Details:
  - Name: {bucket_name}
  - Region: {region}
  - Access: Public read enabled
  - CORS: Configured for web access

Your audio files will be stored at:
  https://{bucket_name}.s3.{region}.amazonaws.com/audio/

Next Steps:
  1. Start your backend server: python app.py
  2. Upload audio files through the API
  3. Files will be automatically stored in S3

Note: Make sure your AWS IAM user has the following permissions:
  - s3:CreateBucket
  - s3:PutObject
  - s3:GetObject
  - s3:DeleteObject
  - s3:PutBucketPolicy
  - s3:PutBucketCORS
  - s3:DeletePublicAccessBlock
""")


def main():
    """Main setup function"""
    print_header("AWS S3 Bucket Setup for Classroom Assistant")
    
    print("""
This script will set up your AWS S3 bucket for storing audio files.

Prerequisites:
  1. AWS account with S3 access
  2. IAM user with S3 permissions
  3. Access key and secret key configured in .env file
""")
    
    # Step 1: Verify credentials
    if not verify_credentials():
        return 1
    
    # Step 2: Create bucket
    if not create_bucket():
        logger.error("\n❌ Bucket setup failed")
        return 1
    
    # Step 3: Test access
    if not test_bucket_access():
        logger.warning("\n⚠️  Bucket created but access test failed")
        logger.info("You may need to check your IAM permissions")
        return 1
    
    # Print summary
    print_summary()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
