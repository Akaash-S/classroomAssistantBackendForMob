#!/bin/bash
# Bash script to restart Docker containers with updated configuration
# This ensures all environment variables are properly loaded

echo "========================================"
echo "  Restarting Classroom Assistant Docker"
echo "========================================"
echo ""

# Stop containers
echo "Stopping containers..."
docker-compose down

# Rebuild (optional - uncomment if you changed Dockerfile)
# echo "Rebuilding images..."
# docker-compose build --no-cache

# Start containers
echo "Starting containers..."
docker-compose up -d

# Wait a moment for containers to start
echo "Waiting for containers to start..."
sleep 5

# Check status
echo ""
echo "Container Status:"
docker-compose ps

# Show logs
echo ""
echo "Recent logs (press Ctrl+C to exit):"
docker-compose logs -f backend
