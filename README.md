# AI Video Editor Platform - Complete Production-Ready Setup

A comprehensive AI-powered video editing platform that allows users to upload videos and photos, describe their desired edits with natural language, and receive automatically generated edited videos.

## Features

- **User Authentication**: JWT-based authentication with secure password hashing
- **Project Management**: Create, edit, and delete video editing projects
- **Asset Management**: Upload videos and images with direct S3 upload support
- **AI-Powered Editing**:
  - Automatic scene detection using PySceneDetect
  - Object recognition using YOLOv8
  - Natural language prompt parsing with Ollama/Llama3
  - Intelligent shot selection using dynamic programming
  - Professional video rendering with filters, transitions, and music
- **Async Processing**: Celery-based background job processing
- **Scalable Architecture**: Containerized with Docker, easily deployable
- **Modern UI**: React-based responsive frontend with Tailwind CSS

## Technology Stack

### Frontend
- React 18
- React Router 6
- Tailwind CSS
- Axios
- React Dropzone
- React Player

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- Pydantic validation
- JWT Authentication
- PostgreSQL
- Celery + Redis
- Boto3 (S3)

### AI & Processing
- PySceneDetect - Scene detection
- YOLOv8 - Object detection
- Ollama with Llama3 - LLM for prompt parsing
- MoviePy - Video rendering
- FFmpeg - Video processing

### Infrastructure
- Docker & Docker Compose
- PostgreSQL
- Redis
- MinIO (S3-compatible storage)
- Nginx (Optional reverse proxy)

## Prerequisites

1. **Docker & Docker Compose**: [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
2. **Ollama** (for AI prompt parsing): [Download Ollama](https://ollama.ai/)
3. **Git**: For version control
4. **System Requirements**:
   - 4GB RAM minimum (8GB recommended)
   - 20GB free disk space
   - GPU optional but recommended for faster video processing

## Quick Start

### 1. Clone or Navigate to Project

```bash
cd ai_video_editor_platform
```

### 2. Environment Setup

Copy the example environment file and customize:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` to customize settings (especially `SECRET_KEY` for production):

```env
SECRET_KEY=your-very-long-secret-key-minimum-32-characters-change-this

# For development, keep other defaults
# For production, update CORS_ORIGINS, database credentials, etc.
```

### 3. Start Ollama (Optional but Recommended)

For AI-powered prompt parsing, start Ollama in a separate terminal:

```bash
ollama pull llama3
ollama serve
```

If Ollama is not available, the system will fall back to rule-based prompt parsing.

### 4. Start Docker Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache and broker
- MinIO object storage
- FastAPI backend
- Celery worker
- React frontend

### 5. Initialize Database (First Time Only)

```bash
docker-compose exec backend python -c "from app.database import init_db; init_db(); print('Database initialized!')"
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (Username: minioadmin, Password: minioadmin)
- **Redis Commander** (optional): Install redis-commander for visualization

## First Run Steps

1. Navigate to http://localhost:3000
2. Register a new account
3. Create a new project
4. Upload a video or image
5. Enter an editing prompt (e.g., "Make it 30 seconds with vintage filter and upbeat music")
6. Click "Start Editing" and wait for processing

## Project Structure

```
ai_video_editor_platform/
├── backend/
│   ├── app/
│   │   ├── auth/          # JWT authentication
│   │   ├── projects/      # Project management
│   │   ├── assets/        # File upload/download
│   │   ├── jobs/          # Job management
│   │   ├── main.py        # FastAPI app
│   │   ├── models.py      # Database models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── config.py      # Configuration
│   │   └── database.py    # Database setup
│   ├── workers/
│   │   ├── celery_app.py  # Celery configuration
│   │   └── tasks.py       # Background tasks
│   ├── ai_engine/
│   │   ├── scene_detector.py
│   │   ├── object_tagger.py
│   │   ├── prompt_parser.py
│   │   ├── shot_selector.py
│   │   ├── renderer.py
│   │   └── assets/        # Background music
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # Auth context
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API services
│   │   ├── App.js         # Main app
│   │   └── index.js       # Entry point
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
└── docker-compose.yml
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token

### Projects
- `GET /api/projects` - List user's projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Assets
- `POST /api/assets/presigned-url` - Get S3 upload URL
- `POST /api/assets/confirm-upload/{project_id}` - Confirm file upload
- `GET /api/assets/project/{project_id}` - List project assets
- `DELETE /api/assets/{id}` - Delete asset

### Jobs
- `POST /api/jobs/project/{project_id}/start-edit` - Start editing job
- `GET /api/jobs/{id}` - Get job status
- `GET /api/jobs/project/{project_id}/latest` - Get latest job

## Configuration

### Environment Variables

Key variables in `backend/.env`:

```env
# Security
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# S3/MinIO
S3_ENDPOINT_URL=http://minio:9000
S3_BUCKET=ai-video-editor

# Celery
CELERY_BROKER_URL=redis://redis:6379/0

# Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend Configuration

Set API URL in `frontend/src/services/api.js` or environment variable:

```bash
REACT_APP_API_URL=http://localhost:8000
```

## Common Tasks

### View Logs

```bash
# Backend logs
docker-compose logs -f backend

# Worker logs
docker-compose logs -f worker

# Frontend logs
docker-compose logs -f frontend

# All logs
docker-compose logs -f
```

### Access Database

```bash
# PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_video_editor

# Redis CLI
docker-compose exec redis redis-cli
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Remove Everything (Clean Slate)

```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If port 8000, 3000, etc. are already in use, edit `docker-compose.yml`:

```yaml
backend:
  ports:
    - "8001:8000"  # Changed from 8000:8000
```

### Database Connection Error

Ensure PostgreSQL is running:

```bash
docker-compose ps postgres

# If not running:
docker-compose up -d postgres
```

### Video Processing Fails

1. Check worker logs: `docker-compose logs worker`
2. Ensure FFmpeg is installed in backend container
3. Check temp directory permissions
4. Verify S3/MinIO connectivity

### Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull Llama3 model
ollama pull llama3
```

If Ollama is unavailable, the system will fall back to rule-based prompt parsing.

### Frontend Can't Connect to Backend

Check CORS settings in `backend/.env`:

```env
CORS_ORIGINS=["http://localhost:3000"]
```

## Deployment for Production

### 1. Update Environment Variables

```bash
cp backend/.env.example backend/.env
# Edit with production values
nano backend/.env
```

Key changes for production:
- Set `DEBUG=False`
- Use strong `SECRET_KEY` (32+ characters)
- Use production database URL
- Update CORS origins
- Use AWS S3 instead of MinIO
- Set up proper SSL certificates

### 2. Use Production Docker Compose Profile

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Or manually configure Nginx with SSL.

### 3. Database Migrations

Create a migration file and run:

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Worker Scaling

To add more workers:

```bash
docker-compose up -d --scale worker=4
```

### 5. Monitoring

Consider adding:
- Prometheus for metrics
- ELK Stack for logging
- Sentry for error tracking

## Background Music Asset

The system expects background music files in `backend/ai_engine/assets/`:

```
backend/ai_engine/assets/
├── upbeat.mp3
├── calm.mp3
└── cinematic.mp3
```

If files don't exist, the system will skip music. Add your royalty-free music files:

1. Download from [Free Music Archive](https://freemusicarchive.org/) or [Pixabay](https://pixabay.com/music/)
2. Place in `backend/ai_engine/assets/`
3. Name according to mood

## Performance Optimization

### For Large Videos
- Increase `VIDEO_PRESET` to `fast` in `.env`
- Reduce sample rate in object tagging
- Use scene detection to split long videos

### For Faster Rendering
- Use GPU acceleration (set up CUDA)
- Adjust bitrate settings
- Pre-process videos to optimal format

### For Scalability
- Scale workers: `docker-compose up -d --scale worker=N`
- Use managed database services
- Implement result caching
- Use CDN for video delivery

## Security Considerations

1. **Change Default Passwords**:
   ```bash
   # MinIO credentials
   # Database password
   # JWT SECRET_KEY
   ```

2. **Enable HTTPS**: Configure SSL certificates in Nginx

3. **Database Security**:
   - Use strong passwords
   - Enable PostgreSQL SSL connections
   - Restrict network access

4. **API Security**:
   - Implement rate limiting
   - Add CSRF protection
   - Validate file uploads
   - Sanitize user inputs

5. **File Upload Limits**:
   ```env
   MAX_FILE_SIZE=524288000  # 500MB
   ```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally with `docker-compose`
4. Commit with clear messages
5. Submit PR

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check logs: `docker-compose logs -f`
2. Review troubleshooting section
3. Check GitHub issues
4. Contact: support@yourcompany.com

## Future Enhancements

- [ ] Multi-language support for prompts
- [ ] Advanced video effects library
- [ ] Real-time collaboration
- [ ] Video templates
- [ ] Custom AI model training
- [ ] Mobile app
- [ ] WebSocket real-time updates
- [ ] Advanced analytics
- [ ] Video import from cloud storage
- [ ] Export to multiple formats

---

**Version**: 1.0.0
**Last Updated**: 2024
**Status**: Production Ready
