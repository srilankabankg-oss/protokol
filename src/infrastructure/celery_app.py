from celery import Celery

from src.infrastructure.config import get_settings

settings = get_settings()

celery_app = Celery(
    "protokol",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "src.adapters.services.meeting_service",
        "src.adapters.services.task_service",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)