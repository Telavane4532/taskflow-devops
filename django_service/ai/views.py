from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from core.models import Task

from .models import AIRequestLog, TaskEmbedding
from .serializers import ParseSerializer, PrioritizeSerializer, SimilarSerializer, SummarizeSerializer
from .services import ModerationError, cosine_similarity, parse_task, prioritize, summarize, upsert_embedding


class AIRateThrottle(UserRateThrottle):
    scope = "ai"


class QuotaMixin:
    feature_name = ""

    def check_feature(self):
        return settings.AI_FEATURE_FLAGS.get(self.feature_name, False)

    def check_daily_quota(self, user):
        used = AIRequestLog.objects.filter(user=user, created_at__date=timezone.now().date()).count()
        return used < settings.AI_DAILY_REQUEST_LIMIT


class SummarizeView(APIView, QuotaMixin):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIRateThrottle]
    feature_name = "summarize"

    def post(self, request):
        if not self.check_feature():
            return Response({"error": "Feature disabled"}, status=status.HTTP_404_NOT_FOUND)
        if not self.check_daily_quota(request.user):
            return Response({"error": "Daily AI quota exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer = SummarizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_id = serializer.validated_data.get("task_id")
        text = serializer.validated_data.get("text")
        task = None
        try:
            if task_id:
                task = Task.objects.get(id=task_id, project__owner=request.user)
                text = f"{task.title}\n{task.description}"
            if not text:
                return Response({"error": "text or task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            summary = summarize(request.user, text)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except ModerationError:
            return Response({"error": "Input blocked by moderation policy"}, status=status.HTTP_400_BAD_REQUEST)
        if task:
            task.ai_summary = summary
            task.save(update_fields=["ai_summary", "updated_at"])
        return Response({"summary": summary})


class PrioritizeView(APIView, QuotaMixin):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIRateThrottle]
    feature_name = "prioritize"

    def post(self, request):
        if not self.check_feature():
            return Response({"error": "Feature disabled"}, status=status.HTTP_404_NOT_FOUND)
        if not self.check_daily_quota(request.user):
            return Response({"error": "Daily AI quota exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer = PrioritizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_id = serializer.validated_data.get("task_id")
        title = serializer.validated_data.get("title")
        description = serializer.validated_data.get("description", "")
        task = None
        try:
            if task_id:
                task = Task.objects.get(id=task_id, project__owner=request.user)
                title, description = task.title, task.description
            if not title:
                return Response({"error": "title or task_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            score = prioritize(request.user, title, description)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except ModerationError:
            return Response({"error": "Input blocked by moderation policy"}, status=status.HTTP_400_BAD_REQUEST)
        if task:
            task.priority_score = score
            task.save(update_fields=["priority_score", "updated_at"])
        return Response({"priority_score": score})


class ParseTaskView(APIView, QuotaMixin):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIRateThrottle]
    feature_name = "parse"

    def post(self, request):
        if not self.check_feature():
            return Response({"error": "Feature disabled"}, status=status.HTTP_404_NOT_FOUND)
        if not self.check_daily_quota(request.user):
            return Response({"error": "Daily AI quota exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer = ParseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            data = parse_task(request.user, serializer.validated_data["text"])
        except ModerationError:
            return Response({"error": "Input blocked by moderation policy"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data)


class SimilarTasksView(APIView, QuotaMixin):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AIRateThrottle]
    feature_name = "similar"

    def post(self, request, task_id: int):
        if not self.check_feature():
            return Response({"error": "Feature disabled"}, status=status.HTTP_404_NOT_FOUND)
        if not self.check_daily_quota(request.user):
            return Response({"error": "Daily AI quota exceeded"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer = SimilarSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        top_k = serializer.validated_data["top_k"]

        try:
            task = Task.objects.get(id=task_id, project__owner=request.user)
            upsert_embedding(task)
            source = TaskEmbedding.objects.get(task=task)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        candidates = TaskEmbedding.objects.filter(task__project__owner=request.user).exclude(task=task).select_related("task")
        ranked = []
        for candidate in candidates:
            ranked.append(
                {
                    "task_id": candidate.task_id,
                    "title": candidate.task.title,
                    "score": round(cosine_similarity(source.vector, candidate.vector), 4),
                }
            )

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return Response({"results": ranked[:top_k]})
