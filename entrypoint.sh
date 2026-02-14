#!/bin/sh
set -e

# Get the PORT from environment, default to 8000
PORT=${PORT:-8000}

echo "AI Video Editor Platform - Starting..."
echo "Port: $PORT"

# Initialize database
echo "Initializing database..."
cd /app/backend
python -c "from app.database import init_db; init_db()" 2>&1 || true

# Start uvicorn
echo "Starting backend API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 4 --access-log
