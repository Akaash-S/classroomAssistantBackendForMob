#!/bin/bash

# Docker Database Container Fix Script
# Run this on your EC2 instance to fix the unhealthy database container

set -e

echo "=========================================="
echo "Docker Database Container Fix Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in backend directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found${NC}"
    echo "Please run this script from the backend directory"
    exit 1
fi

# Step 1: Check .env file
echo -e "${YELLOW}Step 1: Checking .env file...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Creating template .env file..."
    cat > .env << 'EOF'
# Database Configuration
DB_NAME=classroom_assistant
DB_USER=postgres
DB_PASSWORD=CHANGE_THIS_PASSWORD

# Flask Configuration
SECRET_KEY=CHANGE_THIS_SECRET_KEY
FLASK_ENV=production

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=classroom-assistant-audio

# AI Services
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key

# CORS
CORS_ORIGINS=*
EOF
    echo -e "${YELLOW}Template .env file created. Please edit it with your actual values:${NC}"
    echo "  nano .env"
    exit 1
fi

# Check if DB_PASSWORD is set
if grep -q "CHANGE_THIS_PASSWORD" .env; then
    echo -e "${RED}Error: Please set DB_PASSWORD in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env file exists${NC}"

# Step 2: Stop all containers
echo ""
echo -e "${YELLOW}Step 2: Stopping all containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Containers stopped${NC}"

# Step 3: Remove old volumes (optional - asks user)
echo ""
echo -e "${YELLOW}Step 3: Clean up old volumes?${NC}"
echo "This will delete all database data. Only do this if you want a fresh start."
read -p "Remove old volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down -v
    echo -e "${GREEN}✓ Volumes removed${NC}"
else
    echo -e "${YELLOW}Keeping existing volumes${NC}"
fi

# Step 4: Check port availability
echo ""
echo -e "${YELLOW}Step 4: Checking port 5432...${NC}"
if sudo netstat -tulpn | grep -q ":5432 "; then
    echo -e "${RED}Warning: Port 5432 is in use${NC}"
    echo "Checking if it's PostgreSQL service..."
    if sudo systemctl is-active --quiet postgresql; then
        echo "Stopping PostgreSQL service..."
        sudo systemctl stop postgresql
        sudo systemctl disable postgresql
        echo -e "${GREEN}✓ PostgreSQL service stopped${NC}"
    fi
else
    echo -e "${GREEN}✓ Port 5432 is available${NC}"
fi

# Step 5: Start database only
echo ""
echo -e "${YELLOW}Step 5: Starting database container...${NC}"
docker-compose up -d db

# Step 6: Wait for database to be ready
echo ""
echo -e "${YELLOW}Step 6: Waiting for database to be healthy...${NC}"
echo "This may take up to 30 seconds..."

COUNTER=0
MAX_TRIES=30

while [ $COUNTER -lt $MAX_TRIES ]; do
    if docker exec classroom-db pg_isready -U postgres >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Database is healthy!${NC}"
        break
    fi
    
    echo -n "."
    sleep 1
    COUNTER=$((COUNTER + 1))
    
    if [ $COUNTER -eq $MAX_TRIES ]; then
        echo ""
        echo -e "${RED}Error: Database failed to become healthy${NC}"
        echo ""
        echo "Showing database logs:"
        docker-compose logs --tail=50 db
        exit 1
    fi
done

# Step 7: Check database logs
echo ""
echo -e "${YELLOW}Step 7: Checking database logs...${NC}"
if docker-compose logs db | grep -i error; then
    echo -e "${YELLOW}Found errors in logs (shown above)${NC}"
else
    echo -e "${GREEN}✓ No errors in database logs${NC}"
fi

# Step 8: Start all services
echo ""
echo -e "${YELLOW}Step 8: Starting all services...${NC}"
docker-compose up -d

# Step 9: Wait for backend
echo ""
echo -e "${YELLOW}Step 9: Waiting for backend to be ready...${NC}"
sleep 10

# Step 10: Verify all containers
echo ""
echo -e "${YELLOW}Step 10: Verifying all containers...${NC}"
docker-compose ps

# Step 11: Test health endpoint
echo ""
echo -e "${YELLOW}Step 11: Testing API health endpoint...${NC}"
sleep 5

if curl -f http://localhost:5000/api/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${YELLOW}Warning: API health check failed${NC}"
    echo "This might be normal if the backend is still starting up"
fi

# Final status
echo ""
echo "=========================================="
echo -e "${GREEN}Fix script completed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check container status: docker-compose ps"
echo "2. View logs: docker-compose logs -f"
echo "3. Test API: curl http://localhost:5000/api/health"
echo ""
echo "If issues persist, check: DOCKER_DB_TROUBLESHOOTING.md"
