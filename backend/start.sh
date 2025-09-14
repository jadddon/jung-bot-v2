#!/bin/bash
# Jung AI Backend - Railway Startup Script

# Use Railway's PORT environment variable, default to 8000 if not set
# Handle case where PORT might be set but empty or invalid
if [ -z "$PORT" ] || [ "$PORT" = "\$PORT" ]; then
    PORT=8000
fi

# Ensure PORT is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Warning: PORT is not numeric ($PORT), defaulting to 8000"
    PORT=8000
fi

echo "Starting Jung AI Backend on port $PORT"

# Start the application
python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1 --access-log --log-level info 