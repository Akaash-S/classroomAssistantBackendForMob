#!/bin/bash

# Deployment script for Render
# This script helps prepare and deploy the backend to Render

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        Render Deployment Helper                             ║"
echo "║        Classroom Assistant Backend                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}Error: Please run this script from the backend directory${NC}"
    exit 1
fi

echo "Step 1: Checking Prerequisites"
echo "================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}⚠ Git not initialized${NC}"
    read -p "Initialize git repository? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        echo -e "${GREEN}✓ Git initialized${NC}"
    fi
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Please create .env file with required variables"
    exit 1
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check if AWS credentials are set
if grep -q "AWS_ACCESS_KEY_ID=your-aws-access-key-id" .env; then
    echo -e "${YELLOW}⚠ AWS credentials not configured in .env${NC}"
    echo "Please update .env with your AWS credentials"
    exit 1
else
    echo -e "${GREEN}✓ AWS credentials configured${NC}"
fi

echo ""
echo "Step 2: Testing S3 Connection"
echo "================================"

# Test S3 connection
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

echo "Running S3 storage test..."
if $PYTHON_CMD test_s3_storage.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ S3 storage test passed${NC}"
else
    echo -e "${YELLOW}⚠ S3 storage test failed${NC}"
    echo "You may need to run: python setup_s3_bucket.py"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Step 3: Preparing for Deployment"
echo "================================"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}✗ Dockerfile not found${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Dockerfile exists${NC}"
fi

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo -e "${YELLOW}⚠ render.yaml not found (optional)${NC}"
else
    echo -e "${GREEN}✓ render.yaml exists${NC}"
fi

echo ""
echo "Step 4: Git Status"
echo "================================"

# Show git status
git status --short

echo ""
read -p "Commit and push changes? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add all files
    git add .
    
    # Commit
    read -p "Enter commit message: " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Deploy to Render with AWS S3 storage"
    fi
    
    git commit -m "$commit_msg"
    
    # Push
    echo "Pushing to GitHub..."
    git push origin main || git push origin master
    
    echo -e "${GREEN}✓ Changes pushed to GitHub${NC}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        Next Steps                                           ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Go to https://dashboard.render.com/"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository"
echo "4. Configure environment variables:"
echo "   - DATABASE_URL"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - AWS_REGION"
echo "   - AWS_S3_BUCKET"
echo "   - RAPIDAPI_KEY"
echo "   - GEMINI_API_KEY"
echo "   - SECRET_KEY"
echo "   - CORS_ORIGINS"
echo "5. Click 'Create Web Service'"
echo ""
echo "For detailed instructions, see RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${GREEN}Deployment preparation complete!${NC}"
