"""Assets (video/image uploads) routes"""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import boto3
from botocore.config import Config
from app.database import get_db
from app.models import User, Project, Asset
from app.schemas import PresignedURLRequest, PresignedURLResponse, AssetResponse
from app.config import settings
from app.auth.jwt import decode_token
from fastapi.security import HTTPBearer, HTTPAuthCredentials

router = APIRouter(prefix="/api/assets", tags=["assets"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_s3_client():
    """Get S3 client"""
    s3_config = Config(
        signature_version='s3v4',
        retries={'max_attempts': 3}
    )

    return boto3.client(
        's3',
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        use_ssl=settings.S3_USE_SSL,
        config=s3_config
    )


@router.post("/presigned-url", response_model=PresignedURLResponse)
async def get_presigned_url(
    req: PresignedURLRequest,
    project_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate presigned URL for direct S3 upload"""
    # Verify project belongs to user
    project = db.query(Project).filter(
        (Project.id == project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Generate unique storage key
    file_ext = os.path.splitext(req.filename)[1]
    storage_key = f"projects/{project_id}/assets/{uuid.uuid4()}{file_ext}"

    # Generate presigned URL
    s3_client = get_s3_client()
    try:
        presigned_url = s3_client.generate_presigned_post(
            Bucket=settings.S3_BUCKET,
            Key=storage_key,
            Fields={"Content-Type": req.content_type},
            Conditions=[
                ["content-length-range", 0, settings.MAX_FILE_SIZE]
            ],
            ExpiresIn=3600  # 1 hour
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")

    return PresignedURLResponse(
        presigned_url=presigned_url['url'],
        storage_key=storage_key
    )


@router.post("/confirm-upload/{project_id}")
async def confirm_upload(
    project_id: int,
    storage_key: str = Query(...),
    file_type: str = Query(...),
    original_filename: str = Query(...),
    file_size: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AssetResponse:
    """Confirm file upload and create asset record"""
    # Verify project belongs to user
    project = db.query(Project).filter(
        (Project.id == project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create asset record
    asset = Asset(
        project_id=project_id,
        type=file_type,
        storage_key=storage_key,
        original_filename=original_filename,
        file_size=file_size
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@router.get("/project/{project_id}", response_model=list[AssetResponse])
async def get_project_assets(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assets for a project"""
    # Verify project belongs to user
    project = db.query(Project).filter(
        (Project.id == project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    assets = db.query(Asset).filter(Asset.project_id == project_id).all()
    return assets


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Verify project belongs to user
    project = db.query(Project).filter(
        (Project.id == asset.project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Delete from S3
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=settings.S3_BUCKET, Key=asset.storage_key)
    except Exception as e:
        # Log but don't fail
        print(f"Warning: Failed to delete S3 object: {str(e)}")

    # Delete from database
    db.delete(asset)
    db.commit()

    return {"message": "Asset deleted successfully"}
