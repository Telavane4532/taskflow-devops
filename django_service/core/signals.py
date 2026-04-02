from django.db.models.signals import post_save
from django.dispatch import receiver

from ai.tasks import refresh_task_embedding
from .models import Task


@receiver(post_save, sender=Task)
def on_task_saved(sender, instance: Task, created, **kwargs):
    refresh_task_embedding.delay(instance.id)
