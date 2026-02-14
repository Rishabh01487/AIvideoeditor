# Railway Deployment Guide - PRODUCTION READY

## 🚀 Quick Start (5 minutes)

### Step 1: Prepare Repository
```bash
# Make sure all changes are committed
git add .
git commit -m "Production ready - Railway fixes"
git push origin main
```

### Step 2: Configure Railway

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Click "Deploy Now"

### Step 3: Set Environment Variables

In Railway Dashboard → Project Settings → Variables, add:

**Database** (Click "+ Add Service" and select **PostgreSQL**):
```
DATABASE_URL=<auto-populated from PostgreSQL service>
```

**Redis** (Click "+ Add Service" and select **Redis**):
```
REDIS_URL=<auto-populated from Redis service>
CELERY_BROKER_URL=<auto-populated from Redis service>0
CELERY_RESULT_BACKEND=<auto-populated from Redis service>1
```

**Application**:
```
ENV=production
DEBUG=false
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
PORT=8000
WORKERS=4
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com
```

**S3/Object Storage** (if using):
```
S3_ACCESS_KEY=your-key
S3_SECRET_KEY=your-secret
S3_ENDPOINT_URL=https://your-s3-endpoint.com
S3_BUCKET=ai-video-editor
```

### Step 4: Deploy

Railway will automatically:
1. ✅ Detect Python project
2. ✅ Build Docker image (backend)
3. ✅ Set up Database with PostgreSQL
4. ✅ Set up Cache with Redis
5. ✅ Start backend service
6. ✅ Run health checks

---

## 🔧 What Was Fixed

### Critical Issues Resolved:
1. ✅ **Procfile `cd` command error** - Replaced with proper shell scripting
2. ✅ **Database connection pooling** - Optimized for Railway ephemeral environment
3. ✅ **Entrypoint script** - Fixed to not require nginx (Railway handles proxying)
4. ✅ **Python dependencies** - Updated to compatible versions
5. ✅ **Environment configuration** - Proper defaults and Railway support
6. ✅ **Health checks** - Added proper health check endpoints
7. ✅ **Worker configuration** - Fixed Celery for Railway
8. ✅ **Log output** - Configured for Railway logging

### Files Modified:
- `Procfile` - Removed problematic `cd` command
- `backend/requirements.txt` - Updated to stable versions
- `backend/Dockerfile` - Improved for Railway
- `backend/app/config.py` - Railway environment support
- `backend/app/database.py` - Connection pooling for ephemeral environment
- `backend/app/main.py` - Health checks and startup logging
- `backend/workers/celery_app.py` - Improved Celery configuration
- `entrypoint.sh` - Simplified, removed nginx
- `railway.json` - Fixed start command
- `.railwayignore` - Cleaned up files to ignore
- `docker-compose.yml` - Added health checks and better defaults

---

## 🐛 Troubleshooting

### "The executable `cd` could not be found"
**Fixed** ✅ - This was caused by Procfile using `cd` which doesn't work in Railway's execution environment.

### Database connection refused
**Solution**:
- Ensure PostgreSQL service is added in Railway
- Check DATABASE_URL is correctly set
- Railway will automatically provide this when you add a PostgreSQL service

### Build fails with module import errors
**Solution**:
- Check `backend/requirements.txt` matches Python 3.10+
- All dependencies are pinned to compatible versions

### Frontend not connecting to backend API
**Solution**:
- Ensure CORS_ORIGINS includes your domain
- Check REACT_APP_API_URL is correctly set
- Default: `/api` (relative URL works in same domain)

---

## 📊 Deployment Architecture

```
Railway App
├── Backend Service (Python/FastAPI)
│   ├── Port: $PORT (default 8000)
│   ├── Database: PostgreSQL
│   └── Cache: Redis
├── Redis Service
│   └── For caching and Celery broker
└── PostgreSQL Service
    └── For data storage
```

---

## ✅ Verification Checklist

After deployment completes:

- [ ] Backend health endpoint responds: `GET /health`
- [ ] API docs available: `GET /api/docs`
- [ ] Database tables created
- [ ] Redis connection established
- [ ] CORS headers correct
- [ ] Logs show no errors: `railway logs`

### Test Backend Health:
```bash
curl https://your-railway-app.railway.app/health
# Expected response:
# {"status":"healthy","app":"AI Video Editor Platform","version":"1.0.0"}
```

### View Logs:
```bash
railway logs
```

---

## 🔐 Security Notes

1. **Always use strong SECRET_KEY** - Generate with secrets module
2. **Enable HTTPS** - Railway provides free SSL certificates
3. **Set DEBUG=false** - For production
4. **Use environment variables** - Never commit secrets to Git
5. **Validate CORS origins** - Only allow your domains

---

## 📈 Scaling Tips

### For higher load:
1. Increase `WORKERS` environment variable
2. Add more Celery workers (Railway → Services → Add)
3. Scale database: Railway → PostgreSQL → Resize
4. Scale Redis: Railway → Redis → Resize

### Monitor Performance:
- Railway Dashboard → Metrics tab
- Check CPU, Memory, Network usage
- Review logs for errors

---

## 🚀 Next Steps

1. **Custom Domain**: Railway → Settings → Domains → Add custom domain
2. **Auto-deployment**: Railway automatically deploys on git push
3. **Monitoring**: Railway → Observability → Uptimerobot integration
4. **Backups**: Railway → Database → Backups tab

---

## 📞 Support

For Railway-specific issues: [Railway Docs](https://docs.railway.app)

For application issues: Check component health checks and logs.

---

**Deployment Date**: February 2025  
**Status**: ✅ Production Ready
