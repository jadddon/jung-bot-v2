#!/bin/bash
# Jung AI Backend - Railway Startup Script

# Use Railway's PORT environment variable, default to 8000 if not set
PORT=${PORT:-8000}

# Start the application
python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1 --access-log --log-level info 