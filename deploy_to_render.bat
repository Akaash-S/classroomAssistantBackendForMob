@echo off
REM Deployment script for Render (Windows)
REM This script helps prepare and deploy the backend to Render

echo ================================================================
echo.
echo        Render Deployment Helper
echo        Classroom Assistant Backend
echo.
echo ================================================================
echo.

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo Error: Please run this script from the backend directory
    exit /b 1
)

echo Step 1: Checking Prerequisites
echo ================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Please create .env file with required variables
    exit /b 1
) else (
    echo [OK] .env file exists
)

REM Check if AWS credentials are set
findstr /C:"AWS_ACCESS_KEY_ID=your-aws-access-key-id" .env >nul
if %errorlevel% equ 0 (
    echo [WARNING] AWS credentials not configured in .env
    echo Please update .env with your AWS credentials
    exit /b 1
) else (
    echo [OK] AWS credentials configured
)

echo.
echo Step 2: Testing S3 Connection
echo ================================
echo.

REM Test S3 connection
echo Running S3 storage test...
python test_s3_storage.py >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] S3 storage test passed
) else (
    echo [WARNING] S3 storage test failed
    echo You may need to run: python setup_s3_bucket.py
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

echo.
echo Step 3: Preparing for Deployment
echo ================================
echo.

REM Check if Dockerfile exists
if not exist "Dockerfile" (
    echo [ERROR] Dockerfile not found
    exit /b 1
) else (
    echo [OK] Dockerfile exists
)

REM Check if render.yaml exists
if not exist "render.yaml" (
    echo [WARNING] render.yaml not found (optional)
) else (
    echo [OK] render.yaml exists
)

echo.
echo Step 4: Git Status
echo ================================
echo.

REM Show git status
git status --short

echo.
set /p commit="Commit and push changes? (y/n): "
if /i "%commit%"=="y" (
    REM Add all files
    git add .
    
    REM Commit
    set /p commit_msg="Enter commit message: "
    if "%commit_msg%"=="" set commit_msg=Deploy to Render with AWS S3 storage
    
    git commit -m "%commit_msg%"
    
    REM Push
    echo Pushing to GitHub...
    git push origin main || git push origin master
    
    echo [OK] Changes pushed to GitHub
)

echo.
echo ================================================================
echo.
echo        Next Steps
echo.
echo ================================================================
echo.
echo 1. Go to https://dashboard.render.com/
echo 2. Click 'New +' -^> 'Web Service'
echo 3. Connect your GitHub repository
echo 4. Configure environment variables:
echo    - DATABASE_URL
echo    - AWS_ACCESS_KEY_ID
echo    - AWS_SECRET_ACCESS_KEY
echo    - AWS_REGION
echo    - AWS_S3_BUCKET
echo    - RAPIDAPI_KEY
echo    - GEMINI_API_KEY
echo    - SECRET_KEY
echo    - CORS_ORIGINS
echo 5. Click 'Create Web Service'
echo.
echo For detailed instructions, see RENDER_DEPLOYMENT_GUIDE.md
echo.
echo [OK] Deployment preparation complete!
echo.
pause
