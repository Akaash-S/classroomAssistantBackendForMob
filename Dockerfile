# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    PORT=10000

# AWS credentials will be passed via environment variables
# No need to copy credential files into the container

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    ca-certificates \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create uploads directory with proper permissions
RUN mkdir -p /app/uploads && \
    chmod 755 /app/uploads

# Make startup script executable
RUN chmod +x start.sh

# Expose port (Render uses PORT environment variable)
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/api/health || exit 1

# Run the application with startup script
CMD ["./start.sh"]
