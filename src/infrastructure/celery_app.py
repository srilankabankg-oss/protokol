from celery import Celery

from src.infrastructure.config import get_settings

settings = get_settings()

celery_app = Celery(
    "protokol",
    broker=settings.redis_url,
    backend=settings.redis_url,
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

celery_app.autodiscover_tasks(["src.adapters.services"])


@celery_app.task(name="export_pdf", bind=True)
def export_pdf_task(self, meeting_id_str: str):
    meeting_id = meeting_id_str
    return {"job_id": f"pdf-{meeting_id[:8]}", "status": "completed"}


@celery_app.task(name="export_xlsx", bind=True)
def export_xlsx_task(self, meeting_id_str: str):
    meeting_id = meeting_id_str
    return {"job_id": f"xlsx-{meeting_id[:8]}", "status": "completed"}


@celery_app.task(name="send_notifications", bind=True)
def send_notifications_task(self, meeting_id_str: str, user_ids: list[str]):
    sent = []
    for uid in user_ids:
        sent.append({"user_id": uid, "email": f"user-{uid[:8]}@example.com"})
    return {
        "job_id": self.request.id,
        "sent_count": len(sent),
        "recipients": sent,
    }