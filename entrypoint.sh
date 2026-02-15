#!/bin/sh

PORT=${PORT:-8000}

echo "=========================================="
echo "AI Video Editor - Minimal Startup"
echo "=========================================="
echo "Port: $PORT"
echo "PID: $$"

# Start uvicorn directly - no blocking checks
exec uvicorn backend.app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 2 \
    --access-log

