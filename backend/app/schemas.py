"""Pydantic schemas for request/response validation"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Asset Schemas
class AssetBase(BaseModel):
    original_filename: str
    type: str  # "video" or "image"


class AssetCreate(AssetBase):
    storage_key: str
    file_size: int


class AssetUpdate(BaseModel):
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    analysis_metadata: Optional[dict] = None


class AssetResponse(AssetBase):
    id: int
    project_id: int
    storage_key: str
    duration: Optional[float]
    width: Optional[int]
    height: Optional[int]
    analysis_metadata: Optional[dict]
    file_size: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    title: str
    prompt: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    output_video_key: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    assets: List[AssetResponse] = []

    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    pass


class JobResponse(JobBase):
    id: int
    project_id: int
    task_id: Optional[str]
    status: str
    result: Optional[dict]
    error: Optional[str]
    progress: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


# S3 Presigned URL Schemas
class PresignedURLRequest(BaseModel):
    filename: str
    content_type: str
    file_size: int


class PresignedURLResponse(BaseModel):
    presigned_url: str
    storage_key: str


# Job Status Schemas
class JobStatusRequest(BaseModel):
    pass


class EditRequest(BaseModel):
    """Request to start video editing"""
    pass
