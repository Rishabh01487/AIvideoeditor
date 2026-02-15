"""Main FastAPI application entry point"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app FIRST (so it can start responding immediately)
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered video editing platform API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
cors_origins = settings.CORS_ORIGINS
if "*" not in cors_origins and os.getenv("ENV") != "production":
    cors_origins.extend(["http://localhost:3000", "http://localhost:80"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints (before routers, so they respond immediately)
@app.get("/health")
async def health_check():
    """Health check endpoint - always returns 200"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "ok",
        "service": "api",
        "environment": settings.ENV
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


# Initialize database on startup (non-blocking)
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Try to initialize database, but don't fail startup if it fails
    try:
        from app.database import init_db
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization warning: {e}")
        logger.info("Database will be initialized on first API call")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME}")


# Include routers AFTER health endpoints
from app.auth.routes import router as auth_router
from app.projects.routes import router as projects_router
from app.assets.routes import router as assets_router
from app.jobs.routes import router as jobs_router

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(assets_router, prefix="/api/assets", tags=["assets"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level="info"
    )
