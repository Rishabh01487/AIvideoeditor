#!/bin/bash

# AI Video Editor Platform - Setup Script
# This script initializes the application for the first time

set -e

echo "=================================="
echo "AI Video Editor Platform Setup"
echo "=================================="
echo ""

# Check Docker
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Desktop."
    exit 1
fi

echo "✓ Docker Compose found"

# Create .env if not exists
if [ ! -f backend/.env ]; then
    echo ""
    echo "Creating backend/.env from template..."
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
    echo "  ⚠️  Please review and update SECRET_KEY in backend/.env"
fi

# Create necessary directories
mkdir -p backend/ai_engine/assets
mkdir -p /tmp/ai_video_editor

echo "✓ Created necessary directories"

# Start services
echo ""
echo "Starting Docker services..."
docker-compose up -d

echo "✓ Services started"

# Wait for PostgreSQL
echo ""
echo "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres &> /dev/null; then
        echo "✓ PostgreSQL is ready"
        break
    fi
    echo "  Attempt $i/30..."
    sleep 2
done

# Initialize database
echo ""
echo "Initializing database..."
docker-compose exec -T backend python -c "from app.database import init_db; init_db(); print('✓ Database initialized')"

# Check services
echo ""
echo "=================================="
echo "Service Status:"
echo "=================================="
docker-compose ps

echo ""
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Access the application at:"
echo "  Frontend:     http://localhost:3000"
echo "  Backend API:  http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  MinIO:        http://localhost:9001"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Register a new account"
echo "  3. Create a project"
echo "  4. Upload a video or image"
echo "  5. Click 'Start Editing'"
echo ""
echo "For help, see README.md"
echo ""

# Prompt for Ollama
echo "Optional: For AI prompt parsing, start Ollama in another terminal:"
echo "  ollama pull llama3"
echo "  ollama serve"
echo ""
