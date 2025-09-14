# Jung AI Backend - Railway Optimized Dockerfile
# Memory-optimized build for Railway 512MB limit

# Use Python image with build tools already installed
FROM python:3.11

# Set environment variables for Railway optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WORKERS=1 \
    MAX_WORKERS=1 \
    WEB_CONCURRENCY=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Make sure scripts are executable
RUN chmod +x /app/scripts/* 2>/dev/null || true
RUN chmod +x /app/start.sh

# Health check for Railway - use PORT environment variable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; import os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/health')" || exit 1

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Run the application with Railway optimization - use Python script for proper PORT handling
CMD ["python", "-c", "import os; import uvicorn; port=int(os.environ.get('PORT', 8000)); print(f'Starting on port {port}'); uvicorn.run('api.main:app', host='0.0.0.0', port=port, workers=1, log_level='info')"] 