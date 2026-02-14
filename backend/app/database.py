"""Database configuration and session management"""
import logging
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

logger = logging.getLogger(__name__)

# Create engine with proper pooling for Railway
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_size=5,  # Reduced for Railway
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,
        "application_name": "ai_video_editor"
    },
    poolclass=pool.QueuePool if not settings.DEBUG else pool.NullPool
)

# Handle connection events for better error handling
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Set up connection on connect"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET search_path TO public")
    cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
