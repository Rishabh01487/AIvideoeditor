# Development Setup Guide

## Prerequisites

- Docker and Docker Compose
- Git
- Ollama (optional, for advanced LLM features)
- Python 3.11+ (for local development)
- Node.js 18+ (for local frontend development)

## Local Development Setup

### Backend Development

1. **Clone repository**:
   ```bash
   cd ai_video_editor_platform
   ```

2. **Create Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   ```

5. **Start PostgreSQL and Redis** (using Docker):
   ```bash
   docker-compose up -d postgres redis minio
   ```

6. **Initialize database**:
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

7. **Run backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

   Backend will be available at http://localhost:8000
   API documentation at http://localhost:8000/docs

### Frontend Development

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```

   Frontend will be available at http://localhost:3000

3. **Build for production**:
   ```bash
   npm run build
   ```

### Running Celery Worker

```bash
cd backend
celery -A workers.celery_app worker --loglevel=info
```

## Docker Development

### Start All Services

```bash
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend
```

### Access Services

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO: http://localhost:9001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Database Access

```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_video_editor

# Redis CLI
docker-compose exec redis redis-cli
```

### Useful Database Queries

```sql
-- List all users
SELECT id, email, username, created_at FROM users;

-- List all projects
SELECT id, user_id, title, status, created_at FROM projects;

-- List all jobs with status
SELECT id, project_id, status, progress, created_at FROM jobs;

-- Check asset storage
SELECT id, project_id, original_filename, type, file_size FROM assets;
```

## Testing

### Backend Unit Tests

```bash
cd backend
pytest tests/ -v
```

### API Testing with curl

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Create project (with token)
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Project",
    "prompt": "Make it 30 seconds"
  }'
```

## Common Development Tasks

### Add New API Endpoint

1. Create route in appropriate module (e.g., `backend/app/projects/routes.py`)
2. Define schema in `backend/app/schemas.py`
3. Import in `backend/app/main.py`
4. Test with FastAPI Swagger UI at `/docs`

### Add New Frontend Component

1. Create component in `frontend/src/components/`
2. Import and use in parent component
3. Use Tailwind CSS for styling
4. Test in development server

### Database Schema Changes

1. Update models in `backend/app/models.py`
2. Create Alembic migration (when implemented)
3. Apply migration
4. Update backend code

### Add AI Engine Feature

1. Create new module in `backend/ai_engine/`
2. Implement processing logic
3. Integrate into `backend/workers/tasks.py`
4. Add configuration to `backend/app/config.py`

## Performance Profiling

### Backend

```bash
# Install profiling tools
pip install flask-profiler py-spy

# Profile with py-spy
py-spy record -o profile.svg -- python app.py
```

### Frontend

1. Use React DevTools Chrome extension
2. Check Performance tab in Chrome DevTools
3. Use Lighthouse for audit

## Debugging

### Backend Debugging with VS Code

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### Frontend Debugging

Use React DevTools and Chrome DevTools for debugging React components and API calls.

## Code Style

### Python Code Style

```bash
# Install formatters
pip install black flake8 isort

# Format code
black backend/

# Check style
flake8 backend/
isort backend/
```

### JavaScript Code Style

```bash
# Install formatters
npm install --save-dev prettier eslint

# Format code
npm run format

# Lint code
npm run lint
```

## CI/CD Setup

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
      redis:
        image: redis:7

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/
```

## Deployment Checklist

- [ ] Update `SECRET_KEY` with strong value
- [ ] Set `DEBUG=False`
- [ ] Update `CORS_ORIGINS` for production domain
- [ ] Configure production database
- [ ] Set up S3 credentials
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Set up logging
- [ ] Load testing
- [ ] Security audit
- [ ] Performance optimization

## Troubleshooting Development

### Port Conflicts

```bash
# Find and kill process using port
lsof -i :8000
kill -9 PID
```

### Docker Issues

```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild containers
docker-compose build --no-cache
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend python -c "from app.database import init_db; init_db()"
```

### Cache Issues

```bash
# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

Happy coding! 🚀
