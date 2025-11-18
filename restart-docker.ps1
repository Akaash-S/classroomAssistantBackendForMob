# PowerShell script to restart Docker containers with updated configuration
# This ensures all environment variables are properly loaded

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Restarting Classroom Assistant Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop containers
Write-Host "Stopping containers..." -ForegroundColor Yellow
docker-compose down

# Rebuild (optional - uncomment if you changed Dockerfile)
# Write-Host "Rebuilding images..." -ForegroundColor Yellow
# docker-compose build --no-cache

# Start containers
Write-Host "Starting containers..." -ForegroundColor Green
docker-compose up -d

# Wait a moment for containers to start
Write-Host "Waiting for containers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check status
Write-Host ""
Write-Host "Container Status:" -ForegroundColor Cyan
docker-compose ps

# Show logs
Write-Host ""
Write-Host "Recent logs (press Ctrl+C to exit):" -ForegroundColor Cyan
docker-compose logs -f backend
