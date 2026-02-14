# COMPLETE TESTING GUIDE FOR AI VIDEO EDITOR PLATFORM

## ⚠️ IMPORTANT: Start Docker First!

Before running any tests, ensure Docker Desktop is running:

**Windows/Mac**:
1. Open Docker Desktop application
2. Wait for it to say "Docker Desktop is running"
3. Then proceed with testing

**Linux**:
```bash
sudo systemctl start docker
```

---

## PHASE 1: SERVICE STARTUP (10 minutes)

### Step 1: Open Terminal/PowerShell
- Windows: Press `Win + X` → PowerShell
- Mac: Cmd + Space → Terminal
- Linux: Use your preferred terminal

### Step 2: Navigate to Project
```bash
cd c:\Users\risha\OneDrive\Desktop\ai_video_editor_platform
```

### Step 3: Start All Services
```bash
docker-compose up -d
```

**Expected Output**:
```
Creating network "ai-video-editor-platform_app-network" with driver "bridge"
Creating ai-video-editor-postgres ... done
Creating ai-video-editor-redis ... done
Creating ai-video-editor-minio ... done
Creating ai-video-editor-minio-init ... done
Creating ai-video-editor-backend ... done
Creating ai-video-editor-worker ... done
Creating ai-video-editor-frontend ... done
```

### Step 4: Check Service Status
```bash
docker-compose ps
```

**Expected Output**: All services showing "Up" status
```
NAME                            STATUS
ai-video-editor-postgres        Up (healthy)
ai-video-editor-redis           Up (healthy)
ai-video-editor-minio           Up (healthy)
ai-video-editor-backend         Up (healthy)
ai-video-editor-worker          Up
ai-video-editor-frontend        Up (healthy)
```

⚠️ **If services are NOT healthy**: Wait 30 seconds and check again
```bash
docker-compose ps
```

---

## PHASE 2: INITIALIZE DATABASE (5 minutes)

### Step 5: Create Database Tables
```bash
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

**Expected Output**:
```
Database tables created successfully
```

**If you see an error**:
```bash
# Wait for postgres to be ready
sleep 15
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### Step 6: Verify Database Connection
```bash
docker-compose exec postgres psql -U postgres -d ai_video_editor -c "SELECT COUNT(*) FROM users;"
```

**Expected Output**:
```
 count
-------
     0
(1 row)
```

---

## PHASE 3: TEST BACKEND API (10 minutes)

### Step 7: Check Backend Health
```bash
curl http://localhost:8000/health
```

**Expected Output**:
```json
{"status":"healthy","app":"AI Video Editor Platform"}
```

### Step 8: View API Documentation
Open in browser: **http://localhost:8000/docs**

**Expected**: Swagger UI page loads with all API endpoints listed

### Step 9: Register Test User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"testuser@example.com\",
    \"username\": \"testuser\",
    \"password\": \"TestPassword123\",
    \"full_name\": \"Test User\"
  }"
```

**Expected Output**:
```json
{
  "id": 1,
  "email": "testuser@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2024-02-13T22:07:23.123456"
}
```

### Step 10: Login User
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"testuser@example.com\",
    \"password\": \"TestPassword123\"
  }"
```

**Expected Output**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {...}
}
```

**Save the token**: Copy the `access_token` value for next steps
```bash
# Windows PowerShell
$TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Linux/Mac bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 11: Create Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Test Project\",
    \"prompt\": \"Make it 30 seconds with vintage filter\"
  }"
```

**Expected Output**:
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Test Project",
  "prompt": "Make it 30 seconds with vintage filter",
  "status": "draft",
  "output_video_key": null,
  "error_message": null,
  "created_at": "2024-02-13T22:07:23.123456",
  "updated_at": "2024-02-13T22:07:23.123456",
  "assets": []
}
```

### Step 12: List Projects
```bash
curl -X GET http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Output**: JSON array with your project

---

## PHASE 4: TEST FRONTEND (10 minutes)

### Step 13: Access Frontend
Open browser: **http://localhost:3000**

**Expected**: Login page loads with "AI Video Editor" title

### Step 14: Register in Frontend
1. Click "Register" tab
2. Fill in form:
   - Email: `frontend@example.com`
   - Username: `frontenduser`
   - Password: `FrontendPassword123`
   - Full Name: `Frontend User`
3. Click "Register"

**Expected**: Redirected to dashboard

### Step 15: Create Project in Frontend
1. Click "New Project" button
2. Enter title: `Frontend Test Project`
3. Enter prompt: `Make it vintage with upbeat music`
4. Click "Create Project"

**Expected**: Project appears in grid

### Step 16: View Project
1. Click "Edit" on the project
2. See upload zone and prompt field

**Expected**: Can see project details

---

## PHASE 5: TEST OBJECT STORAGE (MinIO) (5 minutes)

### Step 17: Access MinIO
Open browser: **http://localhost:9001**

**Credentials**:
- Username: `minioadmin`
- Password: `minioadmin`

**Expected**: MinIO console loads

### Step 18: Browse Bucket
1. Click on `ai-video-editor` bucket
2. See `projects/` folder

**Expected**: Bucket structure visible

---

## PHASE 6: TEST DATABASE (5 minutes)

### Step 19: Connect to Database
```bash
docker-compose exec postgres psql -U postgres -d ai_video_editor
```

You're now in psql interactive shell. Run:

```sql
-- Check users
SELECT id, email, username, created_at FROM users;

-- Check projects
SELECT id, user_id, title, status FROM projects;

-- Check assets
SELECT id, project_id, type, original_filename FROM assets;

-- Exit
\q
```

**Expected**: See data from your test registrations

---

## PHASE 7: TEST REDIS CACHE (2 minutes)

### Step 20: Connect to Redis
```bash
docker-compose exec redis redis-cli
```

You're now in redis-cli. Run:

```
PING
# Expected: PONG

KEYS *
# Expected: List any cached keys

DBSIZE
# Expected: Number of keys in database

exit
```

---

## PHASE 8: VIEW LOGS (5 minutes)

### Step 21: Backend Logs
```bash
docker-compose logs backend
```

**Look for**:
- No ERROR messages
- "Application startup complete"

### Step 22: Worker Logs
```bash
docker-compose logs worker
```

**Look for**:
- No ERROR messages
- "Worker is ready"

### Step 23: Frontend Logs
```bash
docker-compose logs frontend
```

**Look for**:
- No ERROR messages
- Build completed successfully

### Step 24: Real-time Logs
```bash
# Follow logs from all services
docker-compose logs -f

# Press Ctrl+C to stop
```

---

## ✅ FULL TEST CHECKLIST

After completing all phases above, verify:

### Backend Tests
- [ ] Docker services start successfully
- [ ] Database tables created
- [ ] Health endpoint responds
- [ ] User registration works
- [ ] User login returns token
- [ ] Projects can be created
- [ ] Projects can be listed
- [ ] API documentation loads

### Frontend Tests
- [ ] Login page loads
- [ ] User can register
- [ ] Dashboard displays
- [ ] Projects appear after creation
- [ ] Project editor loads
- [ ] Prompt field visible

### Infrastructure Tests
- [ ] MinIO bucket accessible
- [ ] Database contains data
- [ ] Redis responds to PING
- [ ] All services show as healthy
- [ ] No error logs

### Success Criteria
✅ All 21+ checks pass = Application is working!

---

## 🐛 TROUBLESHOOTING

### Docker Services Won't Start
```bash
# Check Docker is running
docker --version

# Start Docker Desktop (Windows/Mac)
# Then retry: docker-compose up -d
```

### Postgres Connection Refused
```bash
# Wait for postgres to be ready
sleep 30
docker-compose ps

# If still not healthy, restart
docker-compose restart postgres
sleep 10
```

### Frontend Shows "Cannot GET /"
```bash
# Clear browser cache
Ctrl+Shift+Delete (or Cmd+Shift+Delete)
# Then refresh
```

### API Returns 401 Unauthorized
```bash
# Token might be expired, get a new one
# Re-run Step 10 (Login) to get fresh token
```

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux

# Or change port in docker-compose.yml
# "8001:8000" instead of "8000:8000"
```

---

## 📊 PERFORMANCE EXPECTATIONS

| Operation | Expected Time |
|-----------|----------------|
| Docker startup | 20-30 seconds |
| Database init | 2-3 seconds |
| API response | <200ms |
| Frontend load | <1 second |
| File upload (1MB) | <5 seconds |

---

## 🎯 NEXT STEPS AFTER TESTING

### If All Tests Pass ✅
1. Read DEVELOPMENT.md for local development
2. Read DEPLOYMENT.md for production setup
3. Test video upload and processing

### If Tests Fail ❌
1. Check error messages carefully
2. Look at docker logs: `docker-compose logs SERVICE_NAME`
3. Review TROUBLESHOOTING section
4. Check TESTING.md in project for detailed diagnostics

---

## STOPPING SERVICES

When done testing:

```bash
# Stop all services (keep data)
docker-compose down

# Stop and delete all data
docker-compose down -v

# Reset everything
docker-compose down -v
docker-compose up -d
```

---

Good luck! Let me know your test results! 🚀
