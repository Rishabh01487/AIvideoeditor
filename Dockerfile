# Multi-service Dockerfile for AI Video Editor Platform
# Multi-stage build to minimize final image size
# Stage 1: Build (builder)
# Stage 2: Runtime (final, <4GB)

# ========== STAGE 1: BUILDER ==========
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./backend_requirements.txt
RUN pip install --user --no-cache-dir -r ./backend_requirements.txt

# Build frontend
RUN apt-get update && apt-get install -y \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

COPY frontend ./frontend
WORKDIR /app/frontend
ARG REACT_APP_API_URL=/api
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm install --legacy-peer-deps && \
    npm run build && \
    rm -rf node_modules

# ========== STAGE 2: RUNTIME ==========
FROM python:3.11-slim

WORKDIR /app

# Install ONLY runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    bash \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy Python code
COPY backend ./backend

# Copy frontend build from builder
COPY --from=builder /app/frontend/build ./frontend/build

# Copy Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create temp directory
RUN mkdir -p /tmp/ai_video_editor

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start both Nginx (frontend) and backend API server
ENTRYPOINT ["/entrypoint.sh"]
