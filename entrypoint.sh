#!/bin/sh
set -e

# Get the PORT from environment, default to 8000
PORT=${PORT:-8000}

echo "=========================================="
echo "AI Video Editor Platform - Starting..."
echo "=========================================="
echo "Port: $PORT"
echo "Working Directory: $(pwd)"
echo "Environment: ${ENV:-production}"

# Initialize database (with error handling)
echo ""
echo "[1/3] Initializing database..."
python -c "from backend.app.database import init_db; init_db()" 2>&1 || echo "⚠️  Database init skipped"

# Start nginx in background if available
echo ""
echo "[2/3] Starting services..."
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

# Start uvicorn backend API (foreground)
echo ""
echo "[3/3] Starting Backend API (port $PORT)..."
echo "=========================================="
echo ""
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT" --workers 4 --access-log
