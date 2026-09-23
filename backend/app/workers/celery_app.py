"""
Celery Worker Application Setup and Configuration.
"""

from celery import Celery
from backend.app.config import settings

celery_app = Celery(
    "videoscribe_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,       # 30 minute hard time limit
    task_soft_time_limit=1500,  # 25 minute soft time limit
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["backend.app.workers"])
