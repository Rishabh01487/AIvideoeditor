# Production Deployment Guide

## Pre-Deployment Checklist

- [ ] All code reviewed and tested
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Database backups configured
- [ ] Monitoring tools set up
- [ ] CDN configured (optional)
- [ ] Email service configured
- [ ] Security audit completed

## AWS Deployment

### Using EC2

1. **Launch EC2 Instance**:
   - Ubuntu 22.04 LTS
   - t3.medium or larger (for video processing)
   - 100GB+ storage
   - Security group: Allow 80, 443

2. **Install Docker**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **Deploy Application**:
   ```bash
   git clone <repository>
   cd ai_video_editor_platform
   cp backend/.env.example backend/.env
   # Edit .env with production values
   docker-compose -f docker-compose.yml up -d
   ```

### Using RDS for Database

Update `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://username:password@your-rds-endpoint.rds.amazonaws.com:5432/ai_video_editor
```

### Using S3 for Object Storage

Update `.env`:

```env
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=YOUR_AWS_ACCESS_KEY
S3_SECRET_KEY=YOUR_AWS_SECRET_KEY
S3_REGION=us-east-1
S3_USE_SSL=True
```

### Using ElastiCache for Redis

Update `.env`:

```env
REDIS_URL=redis://your-elasticache-endpoint.cache.amazonaws.com:6379/0
CELERY_BROKER_URL=redis://your-elasticache-endpoint.cache.amazonaws.com:6379/0
```

## SSL/HTTPS Setup

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx config with certificate paths
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/certs/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/certs/

# Auto-renewal
sudo certbot renew --dry-run
```

### Update Nginx Config

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # Rest of config...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_assets_project_id ON assets(project_id);
CREATE INDEX idx_jobs_project_id ON jobs(project_id);
CREATE INDEX idx_jobs_status ON jobs(status);
```

### Caching Strategy

```python
# Enable Redis caching in backend
from redis import Redis

cache = Redis.from_url(settings.REDIS_URL)
```

### CDN Setup

Configure CloudFront to cache:
- Video files (24 hour TTL)
- API responses with proper headers
- Static frontend assets (1 year TTL)

## Monitoring & Logging

### CloudWatch Setup

```python
# In backend, add CloudWatch logging
import boto3
from pythonjsonlogger import jsonlogger

logs_client = boto3.client('logs')
```

### Prometheus Metrics

Add to backend for monitoring:

```python
from prometheus_client import Counter, Histogram

# Metrics
request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

### ELK Stack Setup

Deploy Elasticsearch, Logstash, Kibana:

```bash
docker-compose -f docker-compose.elk.yml up -d
```

## Backup Strategy

### Database Backups

```bash
# Daily automated backup
0 2 * * * docker-compose exec postgres pg_dump -U postgres ai_video_editor | gzip > /backups/db_$(date +%Y%m%d).sql.gz
```

### S3 Backup

```bash
# Weekly S3 sync
0 3 * * 0 aws s3 sync s3://ai-video-editor s3://ai-video-editor-backup/$(date +%Y%m%d)
```

## Scaling

### Horizontal Scaling

```bash
# Scale workers
docker-compose up -d --scale worker=4

# Load balance across multiple app servers
# Use Load Balancer (ALB/NLB) in AWS
```

### Database Scaling

- Read replicas for PostgreSQL
- Connection pooling with PgBouncer
- Partitioning for large tables

## Security Hardening

### Network Security

```bash
# Security group rules (AWS)
- Allow 443 from 0.0.0.0/0 (HTTPS)
- Allow 80 from 0.0.0.0/0 (HTTP, redirect only)
- Allow 5432 from app-sg only (PostgreSQL)
- Allow 6379 from app-sg only (Redis)
```

### Application Security

```python
# In main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
)
```

### Database Security

```bash
# Strong password policy
ALTER ROLE postgres SET password_encryption = 'scram-sha-256';

# Restrict connections
# Edit pg_hba.conf
host    ai_video_editor    all    0.0.0.0/0    scram-sha-256
```

## Incident Response

### Database Recovery

```bash
# From backup
docker-compose exec postgres psql -U postgres -d ai_video_editor < /backups/db_latest.sql
```

### Service Restart

```bash
docker-compose restart
docker-compose up -d
```

### Log Analysis

```bash
# Check error logs
docker-compose logs backend | grep ERROR
docker-compose logs worker | grep ERROR
```

## Cost Optimization

- Use spot instances for non-critical services
- Auto-scaling for worker processes
- CloudFront caching to reduce origin traffic
- Reserved instances for predictable load

## SLA & Uptime

### Target Metrics
- 99.9% uptime (4.3 hours downtime/month)
- P95 response time < 200ms
- P99 response time < 500ms
- Zero data loss

### Monitoring Dashboards

```bash
# Grafana setup
docker-compose -f docker-compose.monitoring.yml up -d
```

## Compliance & Regulations

- GDPR: User data deletion, privacy policy
- CCPA: Opt-out mechanisms
- HIPAA: If handling health data
- WCAG: Accessibility standards

## Disaster Recovery Plan

1. **RTO** (Recovery Time Objective): 4 hours
2. **RPO** (Recovery Point Objective): 1 hour
3. **Backup**: Daily, retained for 30 days
4. **Failover**: Multi-region setup (optional)
5. **Testing**: Monthly DR drill

## Post-Launch

- Monitor error rates
- Gather user feedback
- Optimize based on metrics
- Plan feature releases
- Maintain security patches
- Regular capacity planning

---

For 24/7 support, consider:
- AWS Support Plan
- PagerDuty for alerts
- Dedicated monitoring team
- Incident response runbooks
