"""Application configuration"""
import os
import logging
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "AI Video Editor Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, alias="DEBUG")
    ENV: str = Field(default="production", alias="ENV")

    # Database - with Railway support
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/ai_video_editor",
        alias="DATABASE_URL"
    )

    # JWT
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-minimum-32-chars-",
        alias="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # S3/MinIO
    S3_ACCESS_KEY: str = Field(default="", alias="S3_ACCESS_KEY")
    S3_SECRET_KEY: str = Field(default="", alias="S3_SECRET_KEY")
    S3_ENDPOINT_URL: str = Field(default="", alias="S3_ENDPOINT_URL")
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str = "ai-video-editor"
    S3_USE_SSL: bool = True

    # Redis - with Railway support
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", alias="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1", alias="CELERY_RESULT_BACKEND")

    # CORS - flexible for deployment
    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000", "http://localhost", "http://localhost:80"],
        alias="CORS_ORIGINS"
    )

    # Ollama (optional - set to empty string if not using)
    OLLAMA_BASE_URL: str = Field(default="", alias="OLLAMA_BASE_URL")
    OLLAMA_MODEL: str = "llama3"

    # File Processing
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    TEMP_DIR: str = "/tmp/ai_video_editor"
    VIDEO_CODEC: str = "libx264"
    VIDEO_PRESET: str = "medium"
    AUDIO_CODEC: str = "aac"
    VIDEO_BITRATE: str = "2500k"
    AUDIO_BITRATE: str = "192k"

    # Server
    PORT: int = Field(default=8000, alias="PORT")
    WORKERS: int = Field(default=4, alias="WORKERS")

    model_config = {
        'env_file': '.env',
        'case_sensitive': True,
        'extra': 'ignore'
    }

    def __init__(self, **data):
        """Initialize settings with validation"""
        super().__init__(**data)
        
        # Ensure temporary directory exists
        os.makedirs(self.TEMP_DIR, exist_ok=True)


# Create settings instance
try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    # Use defaults
    settings = Settings()
