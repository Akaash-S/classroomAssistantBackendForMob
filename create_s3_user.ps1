# PowerShell script to create a new IAM user with S3 access
# Run this if you have AWS CLI configured on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creating New S3 IAM User" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is installed
try {
    $null = Get-Command aws -ErrorAction Stop
    Write-Host "✅ AWS CLI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install AWS CLI or create user manually:"
    Write-Host "See CREATE_NEW_S3_USER.md for manual instructions"
    exit 1
}

# Check if AWS CLI is configured
try {
    $null = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Host "✅ AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not configured" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run: aws configure"
    Write-Host "Or create user manually: See CREATE_NEW_S3_USER.md"
    exit 1
}

Write-Host ""

# Create IAM user
$USERNAME = "classroom-assistant-s3"
Write-Host "Creating IAM user: $USERNAME" -ForegroundColor Yellow

try {
    aws iam create-user --user-name $USERNAME 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ User created: $USERNAME" -ForegroundColor Green
    } else {
        Write-Host "⚠️  User might already exist, continuing..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  User might already exist, continuing..." -ForegroundColor Yellow
}

# Attach S3 Full Access policy
Write-Host ""
Write-Host "Attaching S3 Full Access policy..." -ForegroundColor Yellow

try {
    aws iam attach-user-policy `
        --user-name $USERNAME `
        --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Policy attached" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to attach policy" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Failed to attach policy" -ForegroundColor Red
    exit 1
}

# Create access key
Write-Host ""
Write-Host "Creating access key..." -ForegroundColor Yellow

try {
    $accessKeyJson = aws iam create-access-key --user-name $USERNAME 2>&1 | ConvertFrom-Json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Access key created" -ForegroundColor Green
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "SAVE THESE CREDENTIALS IMMEDIATELY!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        $accessKeyId = $accessKeyJson.AccessKey.AccessKeyId
        $secretAccessKey = $accessKeyJson.AccessKey.SecretAccessKey
        
        Write-Host "Access Key ID: $accessKeyId" -ForegroundColor Yellow
        Write-Host "Secret Access Key: $secretAccessKey" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        
        # Update .env file
        Write-Host "Updating .env file..." -ForegroundColor Yellow
        
        if (Test-Path ".env") {
            # Backup .env
            Copy-Item ".env" ".env.backup"
            Write-Host "✅ Backed up .env to .env.backup" -ForegroundColor Green
            
            # Read .env content
            $envContent = Get-Content ".env"
            
            # Update credentials
            $envContent = $envContent -replace '^AWS_ACCESS_KEY_ID=.*', "AWS_ACCESS_KEY_ID=$accessKeyId"
            $envContent = $envContent -replace '^AWS_SECRET_ACCESS_KEY=.*', "AWS_SECRET_ACCESS_KEY=$secretAccessKey"
            
            # Write back
            $envContent | Set-Content ".env"
            
            Write-Host "✅ Updated .env file" -ForegroundColor Green
            Write-Host ""
            Write-Host "⚠️  IMPORTANT: Change bucket name in .env to something unique!" -ForegroundColor Yellow
            Write-Host "   AWS_S3_BUCKET=classroom-assistant-audio-yourname-2024" -ForegroundColor Yellow
        } else {
            Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
            Write-Host "Please create .env and add:"
            Write-Host ""
            Write-Host "AWS_ACCESS_KEY_ID=$accessKeyId"
            Write-Host "AWS_SECRET_ACCESS_KEY=$secretAccessKey"
            Write-Host "AWS_REGION=ap-south-1"
            Write-Host "AWS_S3_BUCKET=classroom-assistant-audio-yourname-2024"
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "1. Change bucket name in .env to something unique"
        Write-Host "2. Run: python diagnose_s3_issue.py"
        Write-Host "3. Run: docker-compose restart backend"
        Write-Host "4. Try uploading a lecture"
        Write-Host ""
        
    } else {
        Write-Host "❌ Failed to create access key" -ForegroundColor Red
        Write-Host "User might already have 2 access keys (AWS limit)"
        Write-Host ""
        Write-Host "Solution:"
        Write-Host "1. Go to AWS Console → IAM → Users → $USERNAME"
        Write-Host "2. Delete an old access key"
        Write-Host "3. Run this script again"
        exit 1
    }
} catch {
    Write-Host "❌ Failed to create access key" -ForegroundColor Red
    Write-Host "Error: $_"
    exit 1
}
