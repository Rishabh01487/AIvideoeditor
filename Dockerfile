# AI Video Editor - Production Ready Dockerfile
# Uses Python 3.11-slim for minimal image size
# Multi-stage build: compile > minimal runtime

# Cache buster - RANDOM BUILD ID
ARG BUILD_ID=BUILD-2026-2-15-FIXED-EMAIL-VALIDATOR
LABEL build.id=$BUILD_ID

# Stage 1: Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements FIRST
COPY backend/requirements.txt ./

# Install Python dependencies - FORCE FRESH INSTALL
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --user --force-reinstall --no-cache-dir pydantic[email]==2.5.2 && \
    pip install --user --no-cache-dir -r requirements.txt && \
    python3 -c "from email_validator import validate_email; print('✓ Email validator working')" && \
    python3 -c "from pydantic import EmailStr; print('✓ Pydantic EmailStr working')"

# Build frontend if exists
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps && npm run build || echo "Frontend build optional"

# Stage 2: Runtime stage - minimal deployment image
FROM python:3.11-slim

WORKDIR /app

# Install ONLY runtime system dependencies - all must exist in Debian Trixie
# Avoid deprecated packages like libgl1-mesa-glx, libxrender-dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    nginx \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend application
COPY backend ./backend
COPY .env.example .env.example

# Copy frontend build from builder (if exists)
RUN mkdir -p ./frontend/build
COPY --from=builder /app/frontend/build ./frontend/build

# Copy nginx config (if exists)
RUN mkdir -p /etc/nginx/conf.d
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Setup directories
RUN mkdir -p /tmp/ai_video_editor /app/temp /app/ai_engine/models

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/backend:$PYTHONPATH
ENV PORT=8000

EXPOSE 8000 80 443

# Build timestamp to force fresh build
LABEL build.timestamp="2026-02-15"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start services
ENTRYPOINT ["/app/entrypoint.sh"]
