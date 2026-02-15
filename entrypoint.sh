#!/bin/sh

# Get the PORT from environment, default to 8000
PORT=${PORT:-8000}

echo "=========================================="
echo "AI Video Editor Platform - Starting..."
echo "=========================================="
echo "Port: $PORT"
echo "Working Directory: $(pwd)"
echo "Environment: ${ENV:-production}"

# Start nginx in background if available
echo ""
echo "[1/3] Starting services..."
if command -v nginx &> /dev/null; then
    echo "✓ Starting Nginx (frontend proxy on port 80)..."
    nginx -g "daemon off;" > /tmp/nginx.log 2>&1 &
    NGINX_PID=$!
    echo "  Nginx PID: $NGINX_PID"
else
    echo "⚠️  Nginx not found - frontend may not be available"
fi

# Trap to ensure cleanup
trap 'echo "Shutting down services..."; kill $NGINX_PID 2>/dev/null || true' TERM INT

# Initialize database in background (non-blocking)
echo ""
echo "[2/3] Initializing database (async)..."
python -c "
import os
import sys
import logging
logging.getLogger().setLevel(logging.WARNING)
try:
    from backend.app.database import init_db
    init_db()
    print('✓ Database initialized')
except Exception as e:
    print(f'⚠️  Database init will retry: {str(e)[:50]}')
    sys.exit(0)  # Don't fail startup
" 2>&1 || echo "⚠️  Database initialization skipped"

# Start uvicorn backend API (foreground in main process)
echo ""
echo "[3/3] Starting Backend API (port $PORT)..."
echo "=========================================="
echo ""
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT" --workers 2 --access-log

