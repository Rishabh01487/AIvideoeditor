"""SQLAlchemy database models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    class Status(str, enum.Enum):
        DRAFT = "draft"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=True)
    status = Column(Enum(Status), default=Status.DRAFT, index=True)
    output_video_key = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")


class Asset(Base):
    """Asset model for uploaded videos/images"""
    __tablename__ = "assets"

    class AssetType(str, enum.Enum):
        VIDEO = "video"
        IMAGE = "image"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    type = Column(Enum(AssetType), nullable=False)
    storage_key = Column(String(500), nullable=False, index=True)
    original_filename = Column(String(500), nullable=False)
    duration = Column(Float, nullable=True)  # in seconds, for videos
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    analysis_metadata = Column(JSON, nullable=True)  # stores analysis results
    file_size = Column(Integer, nullable=True)  # in bytes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="assets")


class Job(Base):
    """Job model for processing tasks"""
    __tablename__ = "jobs"

    class Status(str, enum.Enum):
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    task_id = Column(String(255), unique=True, nullable=True, index=True)  # Celery task ID
    status = Column(Enum(Status), default=Status.PENDING, index=True)
    result = Column(JSON, nullable=True)  # stores processing results
    error = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)  # 0-100
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="jobs")
