#!/bin/bash

# Exit on any error
set -e

echo "========================================="
echo "Starting Classroom Assistant Backend"
echo "========================================="

# Print environment info
echo "Environment: ${FLASK_ENV:-development}"
echo "Port: ${PORT:-10000}"
echo "Python version: $(python --version)"

# Wait for database to be ready (if DATABASE_URL is set)
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database connection..."
    python -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if db_url:
    # Fix postgres:// to postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    parsed = urlparse(db_url)
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:] if parsed.path else 'postgres',
                sslmode='require'
            )
            conn.close()
            print('✓ Database connection successful!')
            break
        except Exception as e:
            retry_count += 1
            print(f'Database connection attempt {retry_count}/{max_retries}...')
            time.sleep(2)
    
    if retry_count >= max_retries:
        print('✗ Failed to connect to database')
        exit(1)
"
else
    echo "No DATABASE_URL provided, skipping database check"
fi

# Initialize database tables
echo "Initializing database tables..."
python -c "
from app import app, db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with app.app_context():
    try:
        db.create_all()
        logger.info('✓ Database tables created successfully!')
    except Exception as e:
        logger.error(f'✗ Database initialization error: {e}')
        # Don't exit, let the app handle it
"

echo "========================================="
echo "Starting Gunicorn server..."
echo "========================================="

# Start the application with Gunicorn
exec gunicorn \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    app:app
