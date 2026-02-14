# 🚀 RAILWAY DEPLOYMENT GUIDE - FINAL VERSION

## ✅ What Was Fixed

1. **`.railwayignore`** - Removed `Dockerfile` entries so Railway can see and use the Dockerfile
2. **`railway.json`** - Added explicit build configuration (`"builder": "dockerfile"`)
3. **`Dockerfile`** - Added Nginx installation and proper multi-service setup
4. **`entrypoint.sh`** - Created startup script that runs both Nginx (frontend) and backend
5. **`nginx.conf`** - Updated to proxy to `localhost:8000` (same container setup)
6. **`config.py`** - Removed hardcoded secrets, made sensitive values required via env vars
7. **`Procfile`** - Updated web command to use entrypoint script

---

## 🔧 RAILWAY DEPLOYMENT STEPS

### Step 1: Set Environment Variables in Railway

Go to **Railway Dashboard → Your Project → Variables** and set these:

#### **Critical (Must Set)**
```
SECRET_KEY=your-very-secure-random-secret-key-here-minimum-32-chars
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://your-redis-instance:6379/0
```

#### **S3/Storage Configuration** (if using S3)
```
S3_ACCESS_KEY=your-s3-access-key
S3_SECRET_KEY=your-s3-secret-key
S3_ENDPOINT_URL=https://s3.amazonaws.com (for AWS) or your MinIO URL
```

#### **Optional**
```
DEBUG=False
OLLAMA_BASE_URL=  (leave empty if not using)
CORS_ORIGINS=["https://your-railway-domain.up.railway.app"]
```

---

### Step 2: Push Changes to GitHub

```bash
git add .
git commit -m "Fix deployment: Dockerfile, railway.json, entrypoint, config"
git push origin main
```

---

### Step 3: Trigger Railway Deployment

Option A: Push code (Railway auto-deploys on push)
Option B: In Railway Dashboard, click **Deploy**

---

## 📋 WHAT THE NEW ARCHITECTURE DOES

```
Railway Container
├── Nginx (Port 80)
│   ├── Serves: /app/frontend/build/* (static React files)
│   └── Proxies: /api/* → localhost:8000
│
└── Backend API (Port 8000)
    ├── Runs: FastAPI Uvicorn server
    └── Uses: PostgreSQL, Redis (Railway managed services)
```

**When a user visits your Railway app:**
1. Browser requests `https://your-app.up.railway.app`
2. Railway routes to port 80 (Nginx)
3. Nginx serves React static files
4. React makes API requests to `/api/*`
5. Nginx proxies `/api/*` requests to backend on port 8000
6. Backend processes requests

---

## ✨ KEY IMPROVEMENTS

| Issue | Before | After |
|-------|--------|-------|
| Dockerfile handling | Ignored by `.railwayignore` ❌ | Properly used by Railway ✅ |
| Frontend serving | Built but not served ❌ | Served by Nginx ✅ |
| Backend API | Running but no frontend ❌ | Coordinated with frontend ✅ |
| Secrets | Hardcoded defaults ❌ | Environment variable based ✅ |
| Ollama | Hardcoded localhost path ❌ | Optional, configurable ✅ |
| Build detection | Railpack confused ❌ | Explicit dockerfile builder ✅ |

---

## 🧪 VERIFY DEPLOYMENT

Once deployed, check:

1. **Health Check**: `curl https://your-app.up.railway.app/health`
   - Should return: `{"status": "healthy", "app": "AI Video Editor Platform"}`

2. **Frontend**: Visit `https://your-app.up.railway.app`
   - Should load React UI

3. **API Root**: `curl https://your-app.up.railway.app/api/`
   - Should return: `{"app": "AI Video Editor Platform", "version": "1.0.0", "status": "running"}`

4. **Check Logs**: In Railway Dashboard → View Logs
   - Look for: "Starting Nginx" and "Starting backend API"

---

## 🐛 TROUBLESHOOTING

### Build fails with "Railpack could not determine how to build the app"
- ✅ FIXED: `.railwayignore` now allows Dockerfile
- Make sure you pushed the changes

### Frontend not loading
- Check Nginx logs in Railway dashboard
- Verify frontend build folder exists: `/app/frontend/build`
- Check proxy in nginx.conf is correct

### Backend API not responding
- Check if `SECRET_KEY` environment variable is set
- Check if `DATABASE_URL` is correct
- View backend logs in Railway dashboard

### Database connection fails
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is provisioned in Railway
- Format: `postgresql://user:password@host:port/dbname`

---

## 📦 DEPLOYMENT TIMELINE

1. Build Docker image: **3-5 minutes**
2. Download YOLOv8 model: **10-15 minutes** (largest step)
3. Start services: **1-2 minutes**
4. **Total: ~20 minutes**

---

## ✅ YOU'RE READY!

Push your code to GitHub and Railway will automatically:
1. ✅ Detect the Dockerfile
2. ✅ Build the container
3. ✅ Start Nginx on port 80
4. ✅ Start backend API on dynamic PORT
5. ✅ Serve your app at `https://your-app.up.railway.app`

Good luck! 🚀
