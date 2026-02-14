@echo off
REM AI Video Editor Platform - Setup Script for Windows
REM This script initializes the application for the first time

echo ==================================
echo AI Video Editor Platform Setup
echo ==================================
echo.

REM Check Docker
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo X Docker Compose not found. Please install Docker Desktop.
    pause
    exit /b 1
)

echo [OK] Docker Compose found
echo.

REM Create .env if not exists
if not exist backend\.env (
    echo Creating backend\.env from template...
    copy backend\.env.example backend\.env
    echo [OK] Created backend\.env
    echo WARNING: Please review and update SECRET_KEY in backend\.env
)

REM Create necessary directories
if not exist backend\ai_engine\assets mkdir backend\ai_engine\assets
if not exist C:\tmp\ai_video_editor mkdir C:\tmp\ai_video_editor

echo [OK] Created necessary directories
echo.

REM Start services
echo Starting Docker services...
docker-compose up -d

echo [OK] Services started
echo.

REM Wait for PostgreSQL
echo Waiting for PostgreSQL to be ready...
for /L %%i in (1,1,30) do (
    docker-compose exec -T postgres pg_isready -U postgres >nul 2>&1
    if errorlevel 0 (
        echo [OK] PostgreSQL is ready
        goto pgready
    )
    echo Attempt %%i/30...
    timeout /t 2 /nobreak
)

:pgready
echo.
echo Initializing database...
docker-compose exec -T backend python -c "from app.database import init_db; init_db(); print('[OK] Database initialized')"

REM Check services
echo.
echo ==================================
echo Service Status:
echo ==================================
docker-compose ps

echo.
echo ==================================
echo Setup Complete! ^^!
echo ==================================
echo.
echo Access the application at:
echo   Frontend:     http://localhost:3000
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo   MinIO:        http://localhost:9001
echo.
echo Next steps:
echo   1. Open http://localhost:3000 in your browser
echo   2. Register a new account
echo   3. Create a project
echo   4. Upload a video or image
echo   5. Click 'Start Editing'
echo.
echo For help, see README.md
echo.
echo Optional: For AI prompt parsing, start Ollama in another terminal:
echo   ollama pull llama3
echo   ollama serve
echo.
pause
