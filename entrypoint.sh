#!/bin/sh

PORT=${PORT:-8000}

echo "=========================================="
echo "AI Video Editor - Starting Application"
echo "=========================================="
echo "Port: $PORT"
echo "PID: $$"
echo ""

# Ensure temp directory exists
mkdir -p /tmp/ai_video_editor
mkdir -p /app/temp

# Log startup info
echo "Python: $(python3 --version)"
echo "Uvicorn: $(python3 -m pip show uvicorn | grep Version)"
echo ""

# Start uvicorn directly - no blocking checks
echo "Starting Uvicorn..."
exec uvicorn backend.app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 2 \
    --access-log \
    --log-level info

