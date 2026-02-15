"""Main FastAPI application entry point"""
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app IMMEDIATELY - this must not fail
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="AI Video Editor",
        version="1.0.0",
        description="AI-powered video editing platform",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json"
    )
    logger.info("✓ FastAPI app created")
except Exception as e:
    logger.error(f"✗ Failed to create FastAPI app: {e}")
    sys.exit(1)

# Add CORS middleware
try:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all for simplicity
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("✓ CORS middleware added")
except Exception as e:
    logger.error(f"✗ Failed to add CORS: {e}")

# Health check endpoints - MUST respond immediately
@app.get("/health")
async def health_check():
    """Health check - always responds with 200"""
    return {"status": "healthy", "app": "AI Video Editor"}

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {"status": "ok", "service": "api"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"app": "AI Video Editor", "status": "running"}

logger.info("✓ Health endpoints registered")

# Initialize database on startup (non-blocking)
@app.on_event("startup")
async def startup_event():
    """Initialize on startup - gracefully handle failures"""
    logger.info("🚀 App startup event triggered")
    
    try:
        # Import settings
        from app.config import settings
        logger.info(f"✓ Settings loaded: ENV={settings.ENV}, DEBUG={settings.DEBUG}")
    except Exception as e:
        logger.warning(f"⚠️ Settings load warning: {e}")
        return
    
    try:
        # Try to initialize database, but don't fail startup
        from app.database import init_db
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database init warning (will retry on first request): {e}")
        # Don't fail - let first API call trigger initialization

# Load routers on startup (after health endpoints are ready)
try:
    from app.auth.routes import router as auth_router
    from app.projects.routes import router as projects_router
    from app.assets.routes import router as assets_router
    from app.jobs.routes import router as jobs_router
    
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
    app.include_router(assets_router, prefix="/api/assets", tags=["assets"])
    app.include_router(jobs_router, prefix="/api/jobs", tags=["jobs"])
    logger.info("✓ All routers loaded")
except Exception as e:
    logger.warning(f"⚠️ Router load warning: {e}")
    # App still runs with just health endpoints

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 App shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
