"""Jobs routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Project, Job
from app.schemas import JobResponse, EditRequest
from app.auth.jwt import decode_token
from app.workers.tasks import process_edit_job
from fastapi.security import HTTPBearer, HTTPAuthCredentials

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
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


@router.post("/project/{project_id}/start-edit", response_model=JobResponse)
async def start_edit(
    project_id: int,
    req: EditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start video editing for a project"""
    # Verify project belongs to user and has assets
    project = db.query(Project).filter(
        (Project.id == project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.assets:
        raise HTTPException(status_code=400, detail="Project has no assets")

    # Create job record
    job = Job(project_id=project_id, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Dispatch Celery task
    try:
        celery_task = process_edit_job.delay(project_id=project_id, job_id=job.id)
        job.task_id = celery_task.id
        db.commit()
        db.refresh(job)
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to start job: {str(e)}")

    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job status"""
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Verify user owns this job's project
    project = db.query(Project).filter(
        (Project.id == job.project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return job


@router.get("/project/{project_id}/latest", response_model=JobResponse)
async def get_latest_job(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest job for a project"""
    # Verify project belongs to user
    project = db.query(Project).filter(
        (Project.id == project_id) & (Project.user_id == current_user.id)
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job = db.query(Job).filter(
        Job.project_id == project_id
    ).order_by(desc(Job.created_at)).first()

    if not job:
        raise HTTPException(status_code=404, detail="No jobs found for this project")

    return job
