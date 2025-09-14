#!/bin/bash
# Jung AI Backend - Railway Startup Script

# Get PORT from environment, with proper fallback
export PORT=${PORT:-8000}

# Debug output
echo "Environment PORT variable: '$PORT'"
echo "Using port: $PORT"

# Validate PORT is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: PORT '$PORT' is not a valid number, using 8000"
    export PORT=8000
fi

echo "Starting Jung AI Backend on port $PORT"

# Start the application with explicit port
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "$PORT" --workers 1 --log-level info 