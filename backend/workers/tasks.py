"""Celery tasks for video processing"""
import os
import sys
import shutil
import logging
import uuid
from datetime import datetime
from pathlib import Path
import boto3
from botocore.config import Config
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import Base
from app.models import Project, Job, Asset
from ai_engine.scene_detector import detect_scenes
from ai_engine.object_tagger import tag_video, tag_image
from ai_engine.prompt_parser import parse_prompt_with_ollama
from ai_engine.shot_selector import Scene, select_shots
from ai_engine.renderer import render_video
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def download_asset(s3_client, storage_key: str, local_path: str):
    """Download asset from S3"""
    try:
        s3_client.download_file(
            Bucket=settings.S3_BUCKET,
            Key=storage_key,
            Filename=local_path
        )
        logger.info(f"Downloaded {storage_key} to {local_path}")
    except Exception as e:
        raise Exception(f"Failed to download asset: {str(e)}")


def upload_to_s3(s3_client, file_path: str, key: str):
    """Upload file to S3"""
    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket=settings.S3_BUCKET,
            Key=key
        )
        logger.info(f"Uploaded {file_path} to {key}")
    except Exception as e:
        raise Exception(f"Failed to upload to S3: {str(e)}")


@celery_app.task(bind=True, name='process_edit_job')
def process_edit_job(self, project_id: int, job_id: int):
    """
    Main task for processing video edit job.

    Args:
        project_id: ID of the project
        job_id: ID of the job
    """
    db = SessionLocal()
    temp_dir = None

    try:
        logger.info(f"Starting edit job {job_id} for project {project_id}")

        # Get job and project from database
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise Exception(f"Job {job_id} not found")

        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception(f"Project {project_id} not found")

        # Update job status
        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()

        # Create temp directory
        temp_dir = os.path.join(settings.TEMP_DIR, f"job_{job_id}_{uuid.uuid4()}")
        os.makedirs(temp_dir, exist_ok=True)

        # Download assets
        s3_client = get_s3_client()
        assets = db.query(Asset).filter(Asset.project_id == project_id).all()

        if not assets:
            raise Exception("Project has no assets")

        logger.info(f"Processing {len(assets)} assets")

        clips_info = []  # List of (file_path, start, end)
        all_tags = set()

        for asset in assets:
            local_path = os.path.join(temp_dir, f"asset_{asset.id}_{asset.original_filename}")
            download_asset(s3_client, asset.storage_key, local_path)

            if asset.type == "video":
                # Detect scenes
                scenes_data = detect_scenes(local_path)
                logger.info(f"Detected {len(scenes_data)} scenes in video")

                # Tag video
                tags = tag_video(local_path)
                all_tags.update(tags)

                # Store clips
                for start, end in scenes_data:
                    if start < end:  # Valid scene
                        clips_info.append((local_path, start, end))

            elif asset.type == "image":
                # Tag image
                tags = tag_image(local_path)
                all_tags.update(tags)

                # Use full image as a 3-second clip
                clips_info.append((local_path, 0, 3.0))

        logger.info(f"Found {len(clips_info)} clips and tags: {all_tags}")

        # Parse prompt
        parsed_prompt = parse_prompt_with_ollama(project.prompt)
        logger.info(f"Parsed prompt: {parsed_prompt}")

        # Select shots
        scenes_objs = []
        for file_path, start, end in clips_info:
            scene = Scene(
                start=start,
                end=end,
                tags=list(all_tags),
                score=5.0  # Placeholder aesthetic score
            )
            scenes_objs.append(scene)

        selected_clips = select_shots(
            scenes_objs,
            target_duration=parsed_prompt.get('duration'),
            include_tags=parsed_prompt.get('include_tags', []),
            exclude_tags=parsed_prompt.get('exclude_tags', [])
        )

        if not selected_clips:
            raise Exception("No clips selected after filtering")

        # Build clips_info for selected shots
        selected_clips_info = []
        for start, end in selected_clips:
            for file_path, clip_start, clip_end in clips_info:
                if abs(clip_start - start) < 0.1 and abs(clip_end - end) < 0.1:
                    selected_clips_info.append((file_path, start, end))
                    break

        logger.info(f"Selected {len(selected_clips_info)} clips for rendering")

        # Render video
        output_filename = f"project_{project_id}_{uuid.uuid4()}.mp4"
        output_path = os.path.join(temp_dir, output_filename)

        success = render_video(
            clips_info=selected_clips_info,
            output_path=output_path,
            filter_type=parsed_prompt.get('filter', 'none'),
            speed=parsed_prompt.get('speed', 'normal'),
            transition_type=parsed_prompt.get('transition', 'none'),
            music_mood=parsed_prompt.get('music_mood', 'none'),
            text_overlays=parsed_prompt.get('text_overlays', []),
            duration=parsed_prompt.get('duration')
        )

        if not success:
            raise Exception("Video rendering failed")

        # Upload to S3
        output_s3_key = f"projects/{project_id}/output/{output_filename}"
        upload_to_s3(s3_client, output_path, output_s3_key)

        # Update project
        project.status = "completed"
        project.output_video_key = output_s3_key

        # Update job
        job.status = "completed"
        job.result = {
            "output_key": output_s3_key,
            "parsed_prompt": parsed_prompt,
            "clips_count": len(selected_clips_info)
        }
        job.completed_at = datetime.utcnow()

        db.commit()
        logger.info(f"Job {job_id} completed successfully")

        return {"status": "success", "output_key": output_s3_key}

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")

        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = "failed"
                job.error = str(e)
                job.completed_at = datetime.utcnow()

            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = "failed"
                project.error_message = str(e)

            db.commit()
        except Exception as db_e:
            logger.error(f"Failed to update job status: {str(db_e)}")

        raise

    finally:
        db.close()

        # Cleanup temp directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temp directory {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {str(e)}")
