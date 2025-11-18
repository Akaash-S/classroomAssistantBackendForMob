#!/bin/bash
# Script to create a new IAM user with S3 access
# Run this if you have AWS CLI configured

echo "========================================"
echo "Creating New S3 IAM User"
echo "========================================"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    echo ""
    echo "Please install AWS CLI or create user manually:"
    echo "See CREATE_NEW_S3_USER.md for manual instructions"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured"
    echo ""
    echo "Run: aws configure"
    echo "Or create user manually: See CREATE_NEW_S3_USER.md"
    exit 1
fi

echo "✅ AWS CLI is configured"
echo ""

# Create IAM user
USERNAME="classroom-assistant-s3"
echo "Creating IAM user: $USERNAME"

if aws iam create-user --user-name $USERNAME 2>/dev/null; then
    echo "✅ User created: $USERNAME"
else
    echo "⚠️  User might already exist, continuing..."
fi

# Attach S3 Full Access policy
echo ""
echo "Attaching S3 Full Access policy..."
if aws iam attach-user-policy \
    --user-name $USERNAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess; then
    echo "✅ Policy attached"
else
    echo "❌ Failed to attach policy"
    exit 1
fi

# Create access key
echo ""
echo "Creating access key..."
ACCESS_KEY_OUTPUT=$(aws iam create-access-key --user-name $USERNAME 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ Access key created"
    echo ""
    echo "========================================"
    echo "SAVE THESE CREDENTIALS IMMEDIATELY!"
    echo "========================================"
    echo ""
    
    ACCESS_KEY_ID=$(echo $ACCESS_KEY_OUTPUT | grep -o '"AccessKeyId": "[^"]*' | cut -d'"' -f4)
    SECRET_ACCESS_KEY=$(echo $ACCESS_KEY_OUTPUT | grep -o '"SecretAccessKey": "[^"]*' | cut -d'"' -f4)
    
    echo "Access Key ID: $ACCESS_KEY_ID"
    echo "Secret Access Key: $SECRET_ACCESS_KEY"
    echo ""
    echo "========================================"
    echo ""
    
    # Update .env file
    echo "Updating .env file..."
    
    if [ -f ".env" ]; then
        # Backup .env
        cp .env .env.backup
        echo "✅ Backed up .env to .env.backup"
        
        # Update credentials
        sed -i.tmp "s/^AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID/" .env
        sed -i.tmp "s/^AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY/" .env
        rm -f .env.tmp
        
        echo "✅ Updated .env file"
        echo ""
        echo "⚠️  IMPORTANT: Change bucket name in .env to something unique!"
        echo "   AWS_S3_BUCKET=classroom-assistant-audio-yourname-2024"
    else
        echo "⚠️  .env file not found"
        echo "Please create .env and add:"
        echo ""
        echo "AWS_ACCESS_KEY_ID=$ACCESS_KEY_ID"
        echo "AWS_SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY"
        echo "AWS_REGION=ap-south-1"
        echo "AWS_S3_BUCKET=classroom-assistant-audio-yourname-2024"
    fi
    
    echo ""
    echo "========================================"
    echo "Next Steps:"
    echo "========================================"
    echo "1. Change bucket name in .env to something unique"
    echo "2. Run: python diagnose_s3_issue.py"
    echo "3. Run: docker-compose restart backend"
    echo "4. Try uploading a lecture"
    echo ""
    
else
    echo "❌ Failed to create access key"
    echo "User might already have 2 access keys (AWS limit)"
    echo ""
    echo "Solution:"
    echo "1. Go to AWS Console → IAM → Users → $USERNAME"
    echo "2. Delete an old access key"
    echo "3. Run this script again"
    exit 1
fi
