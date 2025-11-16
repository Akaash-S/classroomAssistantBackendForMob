#!/bin/bash

# Deployment Script for Neon Database Configuration
# This script deploys the application using Neon cloud database

set -e

echo "=========================================="
echo "Classroom Assistant - Neon Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env file found${NC}"

# Check if DATABASE_URL is set
if ! grep -q "DATABASE_URL=postgresql://" .env; then
    echo -e "${RED}Error: DATABASE_URL not found in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ DATABASE_URL configured${NC}"

# Stop any running containers
echo ""
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Containers stopped${NC}"

# Build and start backend (without database)
echo ""
echo -e "${YELLOW}Building and starting backend...${NC}"
docker-compose up -d --build backend

# Wait for backend to start
echo ""
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 10

# Check backend status
echo ""
echo -e "${YELLOW}Checking backend status...${NC}"
if docker-compose ps | grep -q "classroom-backend.*Up"; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Showing logs:"
    docker-compose logs backend
    exit 1
fi

# Test API health
echo ""
echo -e "${YELLOW}Testing API health...${NC}"
sleep 5

if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${YELLOW}Warning: API health check failed${NC}"
    echo "Backend might still be starting up..."
fi

# Run database migration
echo ""
echo -e "${YELLOW}Running database migration...${NC}"
if python3 add_avatar_url_column.py; then
    echo -e "${GREEN}✓ Migration completed${NC}"
else
    echo -e "${YELLOW}Migration may have already been run${NC}"
fi

# Final status
echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Services running:"
docker-compose ps
echo ""
echo "Next steps:"
echo "1. Test API: curl http://localhost:5000/api/health"
echo "2. View logs: docker-compose logs -f backend"
echo "3. Access application at: http://your-ec2-ip:5000"
echo ""
echo "Using Neon Database:"
echo "- No local database container"
echo "- Connected to cloud PostgreSQL"
echo "- Check status at: https://console.neon.tech/"
