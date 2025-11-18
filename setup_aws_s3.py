#!/usr/bin/env python3
"""
AWS S3 Setup Script for Classroom Assistant
This script helps you configure AWS S3 for file storage
"""

import os
import sys
from dotenv import load_dotenv, set_key

def main():
    print("=" * 60)
    print("AWS S3 Setup for Classroom Assistant")
    print("=" * 60)
    print()
    
    # Load existing .env
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"Creating {env_file} from .env.example...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', env_file)
        else:
            with open(env_file, 'w') as f:
                f.write("# Classroom Assistant Environment Variables\n")
    
    load_dotenv()
    
    print("Please provide your AWS credentials:")
    print("(You can get these from AWS IAM Console)")
    print()
    
    # Get AWS Access Key ID
    current_key = os.getenv('AWS_ACCESS_KEY_ID', '')
    if current_key and current_key != 'your_aws_access_key_here':
        print(f"Current AWS Access Key ID: {current_key[:10]}...")
        use_current = input("Keep current key? (y/n): ").lower()
        if use_current == 'y':
            access_key = current_key
        else:
            access_key = input("Enter AWS Access Key ID: ").strip()
    else:
        access_key = input("Enter AWS Access Key ID: ").strip()
    
    # Get AWS Secret Access Key
    current_secret = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    if current_secret and current_secret != 'your_aws_secret_key_here':
        print(f"Current AWS Secret Key: {current_secret[:10]}...")
        use_current = input("Keep current secret? (y/n): ").lower()
        if use_current == 'y':
            secret_key = current_secret
        else:
            secret_key = input("Enter AWS Secret Access Key: ").strip()
    else:
        secret_key = input("Enter AWS Secret Access Key: ").strip()
    
    # Get AWS Region
    current_region = os.getenv('AWS_REGION', 'ap-south-1')
    print(f"\nCurrent AWS Region: {current_region}")
    print("Common regions:")
    print("  - ap-south-1 (Mumbai)")
    print("  - us-east-1 (N. Virginia)")
    print("  - us-west-2 (Oregon)")
    print("  - eu-west-1 (Ireland)")
    region = input(f"Enter AWS Region [{current_region}]: ").strip() or current_region
    
    # Get S3 Bucket Name
    current_bucket = os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')
    print(f"\nCurrent S3 Bucket: {current_bucket}")
    bucket = input(f"Enter S3 Bucket Name [{current_bucket}]: ").strip() or current_bucket
    
    # Save to .env
    print("\nSaving configuration to .env...")
    set_key(env_file, 'AWS_ACCESS_KEY_ID', access_key)
    set_key(env_file, 'AWS_SECRET_ACCESS_KEY', secret_key)
    set_key(env_file, 'AWS_REGION', region)
    set_key(env_file, 'AWS_S3_BUCKET', bucket)
    
    print("✓ Configuration saved!")
    print()
    
    # Test connection
    print("Testing AWS S3 connection...")
    try:
        from services.s3_storage import S3StorageService
        
        s3 = S3StorageService()
        
        if s3.is_available():
            print("✓ AWS S3 connection successful!")
            print(f"  Bucket: {s3.bucket_name}")
            print(f"  Region: {s3.aws_region}")
            print()
            
            # Test upload
            test_upload = input("Test file upload? (y/n): ").lower()
            if test_upload == 'y':
                print("Uploading test file...")
                test_content = b"Test file from Classroom Assistant setup"
                url = s3.upload_audio("test_setup.txt", test_content)
                
                if url:
                    print(f"✓ Test upload successful!")
                    print(f"  URL: {url}")
                    print()
                    print("You can access this file at the URL above.")
                else:
                    print("✗ Test upload failed. Check logs for details.")
        else:
            print("✗ AWS S3 connection failed!")
            print("  Please check your credentials and try again.")
            print("  See AWS_S3_SETUP_FIX.md for troubleshooting.")
            
    except Exception as e:
        print(f"✗ Error testing connection: {str(e)}")
        print("  Make sure boto3 is installed: pip install boto3")
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart your backend server")
    print("2. Try uploading a lecture")
    print("3. Check AWS_S3_SETUP_FIX.md for troubleshooting")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        sys.exit(1)
