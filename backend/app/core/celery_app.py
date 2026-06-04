from celery import Celery
from app.core.config import settings
import os

# Initialize Celery
# Note: For Windows local development, solo pool might be required for Celery.
celery_app = Celery(
    "lumine_worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Auto-discover tasks in specific modules
celery_app.autodiscover_tasks(["app.tasks"])
