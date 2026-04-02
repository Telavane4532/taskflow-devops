from django.conf import settings
from django.db import models

from core.models import Task


class AIRequestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feature = models.CharField(max_length=50)
    prompt = models.TextField(blank=True)
    response = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default="ok")
    created_at = models.DateTimeField(auto_now_add=True)


class TaskEmbedding(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="embedding")
    vector = models.JSONField(default=list)
    source_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
