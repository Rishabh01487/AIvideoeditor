"""Celery app configuration"""
import logging
from celery import Celery
from celery.signals import worker_ready, worker_shutdown
from app.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "ai_video_editor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['workers.tasks']
)

# Configure Celery with Railway-friendly settings
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,  # Restart worker after 100 tasks
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
        'ignore_subscribe_error': True
    }
)

# Signal handlers
@worker_ready.connect
def worker_init(sender, **kwargs):
    """Initialize worker"""
    logger.info("Celery worker is ready")

@worker_shutdown.connect
def worker_shutdown_handler(sender, **kwargs):
    """Shutdown handler"""
    logger.info("Celery worker is shutting down")
