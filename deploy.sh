#!/bin/bash

# Simple Deployment Script for EC2 with Neon Database
# Usage: ./deploy.sh

set -e

echo "================================================"
echo "  Classroom Assistant - EC2 Deployment"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env file with required variables"
    exit 1
fi

echo -e "${GREEN}✓ .env file found${NC}"

# Add missing env vars if needed
if ! grep -q "FIREBASE_CREDENTIALS" .env; then
    echo "FIREBASE_CREDENTIALS=" >> .env
    echo -e "${YELLOW}Added FIREBASE_CREDENTIALS to .env${NC}"
fi

if ! grep -q "GOOGLE_CLOUD_PROJECT" .env; then
    echo "GOOGLE_CLOUD_PROJECT=" >> .env
    echo -e "${YELLOW}Added GOOGLE_CLOUD_PROJECT to .env${NC}"
fi

# Stop old containers
echo ""
echo -e "${YELLOW}Stopping old containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Stopped${NC}"

# Start backend (NOT database - using Neon)
echo ""
echo -e "${YELLOW}Starting backend container...${NC}"
docker-compose up -d backend

# Wait for startup
echo ""
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 15

# Check status
echo ""
echo -e "${YELLOW}Checking container status...${NC}"
docker-compose ps

# Check if backend is running
if docker-compose ps | grep -q "classroom-backend.*Up"; then
    echo -e "${GREEN}✓ Backend is running!${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Showing logs:"
    docker-compose logs backend
    exit 1
fi

# Show recent logs
echo ""
echo -e "${YELLOW}Recent logs:${NC}"
docker-compose logs --tail=20 backend

# Test API
echo ""
echo -e "${YELLOW}Testing API...${NC}"
sleep 5

if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding!${NC}"
else
    echo -e "${YELLOW}⚠ API not responding yet (may still be starting)${NC}"
fi

# Success
echo ""
echo "================================================"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Run migration: python3 add_avatar_url_column.py"
echo "2. Test API: curl http://localhost:5000/api/health"
echo "3. View logs: docker-compose logs -f backend"
echo ""
echo "Access your API at:"
echo "  Local: http://localhost:5000"
echo "  Public: http://$(curl -s ifconfig.me):5000"
echo ""
