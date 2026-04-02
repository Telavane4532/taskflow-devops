from celery import shared_task

from core.models import Task

from .services import upsert_embedding


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def refresh_task_embedding(self, task_id: int):
    task = Task.objects.get(id=task_id)
    upsert_embedding(task)
    return {"task_id": task_id, "status": "ok"}
