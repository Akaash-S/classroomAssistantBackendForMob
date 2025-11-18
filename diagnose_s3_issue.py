#!/usr/bin/env python3
"""
S3 Issue Diagnosis Tool
Helps identify the exact problem with S3 access
"""

import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

print("=" * 70)
print("  S3 Issue Diagnosis Tool")
print("=" * 70)

# Get credentials
aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION', 'ap-south-1')
aws_bucket = os.getenv('AWS_S3_BUCKET', 'classroom-assistant-audio')

print("\n1. Checking credentials...")
print(f"   Access Key: {aws_key[:10]}...{aws_key[-4:]}" if aws_key else "   ❌ Not set")
print(f"   Region: {aws_region}")
print(f"   Bucket: {aws_bucket}")

if not aws_key or not aws_secret:
    print("\n❌ Credentials not configured!")
    exit(1)

# Create S3 client
print("\n2. Creating S3 client...")
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=aws_region
    )
    print("   ✅ S3 client created")
except Exception as e:
    print(f"   ❌ Failed: {str(e)}")
    exit(1)

# Test 1: List all buckets (tests basic S3 access)
print("\n3. Testing basic S3 access (list buckets)...")
try:
    response = s3.list_buckets()
    buckets = [b['Name'] for b in response['Buckets']]
    print(f"   ✅ Can access S3! Found {len(buckets)} bucket(s)")
    if buckets:
        print("   Your buckets:")
        for bucket in buckets[:5]:
            print(f"     - {bucket}")
        if len(buckets) > 5:
            print(f"     ... and {len(buckets) - 5} more")
except ClientError as e:
    error_code = e.response['Error']['Code']
    print(f"   ❌ Cannot access S3: {error_code}")
    print(f"   Error: {e.response['Error'].get('Message', 'Unknown error')}")
    print("\n   SOLUTION:")
    print("   1. Go to AWS IAM Console")
    print("   2. Find your IAM user")
    print("   3. Add 'AmazonS3FullAccess' policy")
    exit(1)

# Test 2: Check if target bucket exists
print(f"\n4. Checking if bucket '{aws_bucket}' exists...")
try:
    s3.head_bucket(Bucket=aws_bucket)
    print(f"   ✅ Bucket exists and you have access!")
    bucket_exists = True
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == '404':
        print(f"   ⚠️  Bucket does not exist")
        bucket_exists = False
    elif error_code == '403':
        print(f"   ❌ Bucket exists but ACCESS DENIED")
        print(f"\n   This means:")
        print(f"   - Bucket '{aws_bucket}' is owned by another AWS account")
        print(f"   - OR you don't have permission to access it")
        print(f"\n   SOLUTION:")
        print(f"   Change bucket name in .env to something unique:")
        print(f"   AWS_S3_BUCKET={aws_bucket}-yourname-2024")
        exit(1)
    else:
        print(f"   ❌ Error: {error_code}")
        exit(1)

# Test 3: Try to create bucket if it doesn't exist
if not bucket_exists:
    print(f"\n5. Attempting to create bucket '{aws_bucket}'...")
    try:
        if aws_region == 'us-east-1':
            s3.create_bucket(Bucket=aws_bucket)
        else:
            s3.create_bucket(
                Bucket=aws_bucket,
                CreateBucketConfiguration={'LocationConstraint': aws_region}
            )
        print(f"   ✅ Bucket created successfully!")
        bucket_exists = True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            print(f"   ❌ Bucket name is taken by another AWS account")
            print(f"\n   SOLUTION:")
            print(f"   Use a unique bucket name in .env:")
            print(f"   AWS_S3_BUCKET={aws_bucket}-yourname-2024")
            exit(1)
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"   ✅ Bucket already exists and is owned by you")
            bucket_exists = True
        else:
            print(f"   ❌ Failed to create bucket: {error_code}")
            print(f"   Error: {e.response['Error'].get('Message', 'Unknown')}")
            exit(1)

# Test 4: Try to upload a test file
if bucket_exists:
    print(f"\n6. Testing file upload to '{aws_bucket}'...")
    try:
        test_key = 'test/diagnosis_test.txt'
        test_content = b'Test from diagnosis tool'
        
        s3.put_object(
            Bucket=aws_bucket,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print(f"   ✅ Upload successful!")
        
        # Generate URL
        url = f"https://{aws_bucket}.s3.{aws_region}.amazonaws.com/{test_key}"
        print(f"   📎 URL: {url}")
        
        # Try to make it public
        try:
            s3.put_object_acl(
                Bucket=aws_bucket,
                Key=test_key,
                ACL='public-read'
            )
            print(f"   ✅ File is publicly accessible")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessControlListNotSupported':
                print(f"   ⚠️  ACL not supported (bucket policy will handle access)")
            else:
                print(f"   ⚠️  Could not make file public: {e.response['Error']['Code']}")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"   ❌ Upload failed: {error_code}")
        print(f"   Error: {e.response['Error'].get('Message', 'Unknown')}")
        print(f"\n   SOLUTION:")
        print(f"   Your IAM user needs PutObject permission")
        print(f"   Add 'AmazonS3FullAccess' policy to your IAM user")
        exit(1)

# Test 5: Check IAM permissions
print(f"\n7. Checking IAM permissions...")
try:
    iam = boto3.client(
        'iam',
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
        region_name=aws_region
    )
    
    # Try to get user info
    try:
        user_info = iam.get_user()
        username = user_info['User']['UserName']
        print(f"   ✅ IAM User: {username}")
        
        # Try to list attached policies
        try:
            policies = iam.list_attached_user_policies(UserName=username)
            if policies['AttachedPolicies']:
                print(f"   Attached policies:")
                for policy in policies['AttachedPolicies']:
                    print(f"     - {policy['PolicyName']}")
                    if 'S3' in policy['PolicyName']:
                        print(f"       ✅ Has S3 policy!")
            else:
                print(f"   ⚠️  No policies attached directly")
        except:
            print(f"   ⚠️  Cannot list policies (permission denied)")
            
    except ClientError as e:
        print(f"   ⚠️  Cannot get IAM user info: {e.response['Error']['Code']}")
        
except Exception as e:
    print(f"   ⚠️  Cannot check IAM: {str(e)}")

# Summary
print("\n" + "=" * 70)
print("  DIAGNOSIS COMPLETE")
print("=" * 70)

if bucket_exists:
    print("\n✅ S3 is configured correctly!")
    print("\nNext steps:")
    print("1. Restart your backend:")
    print("   docker-compose restart backend")
    print("2. Try uploading a lecture")
    print("\nIf lecture upload still fails, check backend logs.")
else:
    print("\n❌ S3 configuration has issues")
    print("\nFollow the solutions above to fix the problems.")

print("\n" + "=" * 70)
