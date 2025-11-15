#!/usr/bin/env python3
"""
S3 Issue Diagnosis Script
Helps identify and fix common S3 upload issues
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def check_credentials():
    """Check AWS credentials"""
    print_header("1. Checking AWS Credentials")
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    bucket = os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')
    
    if not access_key or access_key.startswith('your-'):
        print("❌ AWS_ACCESS_KEY_ID not configured")
        return False
    
    if not secret_key or secret_key.startswith('your-'):
        print("❌ AWS_SECRET_ACCESS_KEY not configured")
        return False
    
    print(f"✓ AWS_ACCESS_KEY_ID: {access_key[:4]}...{access_key[-4:]}")
    print(f"✓ AWS_SECRET_ACCESS_KEY: {secret_key[:4]}...{secret_key[-4:]}")
    print(f"✓ AWS_REGION: {region}")
    print(f"✓ AWS_S3_BUCKET: {bucket}")
    
    return True


def check_s3_client():
    """Check S3 client initialization"""
    print_header("2. Checking S3 Client")
    
    try:
        storage = S3StorageService(auto_create_bucket=False)
        
        if not storage.s3_client:
            print("❌ S3 client failed to initialize")
            return False, None
        
        print("✓ S3 client initialized successfully")
        return True, storage
    except Exception as e:
        print(f"❌ Error initializing S3 client: {str(e)}")
        return False, None


def check_bucket_access(storage):
    """Check bucket access"""
    print_header("3. Checking Bucket Access")
    
    try:
        storage.s3_client.head_bucket(Bucket=storage.bucket_name)
        print(f"✓ Bucket {storage.bucket_name} exists and is accessible")
        return True
    except Exception as e:
        error_code = e.response['Error']['Code'] if hasattr(e, 'response') else 'Unknown'
        print(f"❌ Bucket access failed: {error_code}")
        print(f"   Error: {str(e)}")
        
        if error_code == '404':
            print("\n   Bucket does not exist. Attempting to create...")
            if storage.create_bucket():
                print("   ✓ Bucket created successfully")
                return True
            else:
                print("   ❌ Failed to create bucket")
                return False
        elif error_code == '403':
            print("\n   Access denied. Check IAM permissions:")
            print("   - s3:ListBucket")
            print("   - s3:GetBucketLocation")
            print("   - s3:HeadBucket")
            return False
        
        return False


def test_upload(storage):
    """Test file upload"""
    print_header("4. Testing File Upload")
    
    test_content = b"Test audio file content for S3 upload verification"
    test_filename = f"test_upload_{int(os.times().elapsed * 1000)}.m4a"
    
    print(f"Uploading test file: {test_filename}")
    print(f"File size: {len(test_content)} bytes")
    
    try:
        public_url = storage.upload_audio(test_filename, test_content)
        
        if public_url:
            print(f"✓ Upload successful!")
            print(f"  URL: {public_url}")
            return True, test_filename
        else:
            print("❌ Upload failed - no URL returned")
            print("\nCheck backend logs for detailed error messages")
            return False, None
    except Exception as e:
        print(f"❌ Upload failed with exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False, None


def test_public_access(public_url):
    """Test if uploaded file is publicly accessible"""
    print_header("5. Testing Public Access")
    
    if not public_url:
        print("⚠ No URL to test")
        return False
    
    try:
        import requests
        response = requests.head(public_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✓ File is publicly accessible")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            return True
        elif response.status_code == 403:
            print(f"❌ Access Denied (403)")
            print("\nPossible causes:")
            print("  1. Bucket policy not set correctly")
            print("  2. Block Public Access is enabled")
            print("  3. ACL not supported and no bucket policy")
            print("\nSolutions:")
            print("  1. Run: python setup_s3_bucket.py")
            print("  2. Check AWS Console → S3 → Bucket → Permissions")
            print("  3. Disable 'Block all public access'")
            return False
        else:
            print(f"⚠ Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing public access: {str(e)}")
        return False


def cleanup_test_file(storage, filename):
    """Clean up test file"""
    print_header("6. Cleaning Up")
    
    if not filename:
        print("⚠ No file to clean up")
        return
    
    try:
        file_key = f"audio/{filename}"
        if storage.delete_file(file_key):
            print(f"✓ Test file deleted: {filename}")
        else:
            print(f"⚠ Could not delete test file: {filename}")
    except Exception as e:
        print(f"⚠ Error deleting test file: {str(e)}")


def print_recommendations(results):
    """Print recommendations based on test results"""
    print_header("Recommendations")
    
    if all(results.values()):
        print("✅ All tests passed! S3 storage is working correctly.")
        print("\nYour application should be able to upload files successfully.")
        return
    
    print("❌ Some tests failed. Here's what to do:\n")
    
    if not results.get('credentials'):
        print("1. Configure AWS Credentials:")
        print("   - Add AWS_ACCESS_KEY_ID to .env")
        print("   - Add AWS_SECRET_ACCESS_KEY to .env")
        print("   - Restart your application")
    
    if not results.get('client'):
        print("2. Check AWS Credentials:")
        print("   - Verify credentials are correct")
        print("   - Check IAM user exists")
        print("   - Ensure credentials have S3 permissions")
    
    if not results.get('bucket'):
        print("3. Fix Bucket Access:")
        print("   - Run: python setup_s3_bucket.py")
        print("   - Or create bucket manually in AWS Console")
        print("   - Verify bucket name is unique")
    
    if not results.get('upload'):
        print("4. Fix Upload Issues:")
        print("   - Check IAM permissions: s3:PutObject")
        print("   - Verify bucket exists")
        print("   - Check backend logs for detailed errors")
    
    if not results.get('public_access'):
        print("5. Fix Public Access:")
        print("   - Run: python setup_s3_bucket.py")
        print("   - Disable 'Block all public access' in AWS Console")
        print("   - Set bucket policy for public read")
        print("   - Or use signed URLs instead")


def main():
    """Main function"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║        S3 Issue Diagnosis                                   ║")
    print("║        Troubleshooting Upload Failures                      ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Run checks
    results['credentials'] = check_credentials()
    if not results['credentials']:
        print_recommendations(results)
        return 1
    
    results['client'], storage = check_s3_client()
    if not results['client']:
        print_recommendations(results)
        return 1
    
    results['bucket'] = check_bucket_access(storage)
    if not results['bucket']:
        print_recommendations(results)
        return 1
    
    results['upload'], test_filename = test_upload(storage)
    
    if results['upload'] and test_filename:
        # Get the public URL for testing
        public_url = f"https://{storage.bucket_name}.s3.{storage.aws_region}.amazonaws.com/audio/{test_filename}"
        results['public_access'] = test_public_access(public_url)
        cleanup_test_file(storage, test_filename)
    else:
        results['public_access'] = False
    
    # Print recommendations
    print_recommendations(results)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
