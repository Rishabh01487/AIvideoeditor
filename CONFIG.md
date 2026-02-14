# AI Video Editor Platform - Configuration Guide

## Environment Variables Reference

### Backend Configuration

```env
# Application Settings
APP_NAME=AI Video Editor Platform
APP_VERSION=1.0.0
DEBUG=False                              # Set to True for development

# Security
SECRET_KEY=your-min-32-character-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_video_editor

# S3/Object Storage
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_ENDPOINT_URL=http://minio:9000       # For local dev;  use https://s3.amazonaws.com for AWS
S3_REGION=us-east-1
S3_BUCKET=ai-video-editor
S3_USE_SSL=False                         # Set to True for HTTPS

# Redis Cache
REDIS_URL=redis://redis:6379/0

# Celery Task Queue
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# Ollama LLM
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# File Processing
MAX_FILE_SIZE=524288000                  # 500MB in bytes
TEMP_DIR=/tmp/ai_video_editor
VIDEO_CODEC=libx264
VIDEO_PRESET=medium                      # Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
AUDIO_CODEC=aac
VIDEO_BITRATE=2500k
AUDIO_BITRATE=192k
```

### Frontend Configuration

```javascript
// Environment Variables (frontend/.env or .env.local)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_OLLAMA_URL=http://localhost:11434  // Optional
```

## Production Configuration

### AWS S3 Setup

```env
# Replace MinIO with AWS S3
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=YOUR_AWS_ACCESS_KEY_ID
S3_SECRET_KEY=YOUR_AWS_SECRET_ACCESS_KEY
S3_REGION=us-east-1
S3_BUCKET=your-bucket-name
S3_USE_SSL=True
```

### RDS PostgreSQL

```env
DATABASE_URL=postgresql://admin:your-password@your-rds-endpoint.rds.amazonaws.com:5432/ai_video_editor
```

### ElastiCache Redis

```env
REDIS_URL=redis://your-elasticache.cache.amazonaws.com:6379/0?ssl_certfile=/path/to/cert
CELERY_BROKER_URL=redis://your-elasticache.cache.amazonaws.com:6379/0?ssl_certfile=/path/to/cert
```

### Production CORS

```env
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

### Production Security

```env
SECRET_KEY=generate-very-long-random-string-minimum-32-chars-do-not-expose
DEBUG=False
```

## Video Processing Configuration

### Quality Settings

```env
# High Quality (slower rendering)
VIDEO_BITRATE=5000k
VIDEO_PRESET=slower
AUDIO_BITRATE=320k

# Standard Quality (recommended)
VIDEO_BITRATE=2500k
VIDEO_PRESET=medium
AUDIO_BITRATE=192k

# Low Quality (faster rendering, for testing)
VIDEO_BITRATE=1000k
VIDEO_PRESET=faster
AUDIO_BITRATE=96k
```

### File Size Limits

```env
# Maximum 500MB
MAX_FILE_SIZE=524288000

# Maximum 1GB
MAX_FILE_SIZE=1073741824

# Maximum 100MB (for testing)
MAX_FILE_SIZE=104857600
```

## Ollama Configuration

### Model Options

```bash
# Recommended for video editing
ollama pull llama3          # 7B, 4.7GB

# Faster, smaller
ollama pull llama2:7b       # 7B, 3.8GB
ollama pull mistral         # 7B, 4.1GB

# More capable, larger
ollama pull llama3:70b      # 70B, 40GB
```

### Running Ollama

```bash
# Start Ollama server
ollama serve

# Manually run a model
ollama pull llama3
ollama run llama3

# On macOS/Windows
# Download from https://ollama.ai
```

## Docker Configuration

### Performance Tuning

```yaml
# In docker-compose.yml for worker service
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

### Volume Mounts

```yaml
volumes:
  - ./backend:/app              # Source code
  - /tmp/ai_video_editor:/tmp/ai_video_editor  # Temp files
  - postgres_data:/var/lib/postgresql/data     # Database
```

## Troubleshooting Configuration

### Service Dependencies

If services fail to start:

```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs SERVICE_NAME

# Restart services in order
docker-compose down
docker-compose up -d postgres redis minio
docker-compose up -d backend worker frontend
```

### Network Issues

```env
# For Docker on Mac/Windows
OLLAMA_BASE_URL=http://host.docker.internal:11434

# For Docker on Linux
OLLAMA_BASE_URL=http://localhost:11434
```

### Memory Issues

```env
# Reduce video quality
VIDEO_PRESET=faster
VIDEO_BITRATE=1500k

# Reduce Celery concurrency
# In workers/celery_app.py: concurrency=1
```

## API Configuration

### Rate Limiting (Future)

```python
# Add to backend configuration
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD=3600  # per hour
```

### File Upload Configuration

```env
# Pre-signed URL expiry (seconds)
PRESIGNED_URL_EXPIRY=3600

# Allowed file types
ALLOWED_VIDEO_TYPES=["video/mp4", "video/quicktime", "video/x-msvideo"]
ALLOWED_IMAGE_TYPES=["image/jpeg", "image/png", "image/gif"]
```

## Monitoring Configuration (Optional)

### Prometheus

```yaml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
```

### Grafana

```yaml
services:
  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    ports:
      - "3001:3000"
```

## Backup Configuration

```env
# Backup schedule (cron format)
BACKUP_SCHEDULE=0 2 * * *   # Daily at 2 AM

# Retention policy
BACKUP_RETENTION_DAYS=30

# S3 backup location
BACKUP_S3_BUCKET=your-backup-bucket
BACKUP_S3_PREFIX=ai-video-editor/backups/
```

## Email Configuration (Future)

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=noreply@yourdomain.com
```

## Logging Configuration

```python
# Logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log rotation
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

---

**Best Practices**:
1. Never commit `.env` to version control
2. Use strong, unique SECRET_KEY
3. Rotate credentials regularly
4. Monitor logs for errors
5. Test configuration changes locally first
6. Document any custom configurations
