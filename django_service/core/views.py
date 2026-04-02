from rest_framework import permissions, viewsets

from .models import ActivityLog, Comment, Project, Task
from .serializers import ActivityLogSerializer, CommentSerializer, ProjectSerializer, TaskSerializer


class OwnedOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "owner", None)
        if owner is None and hasattr(obj, "task") and hasattr(obj.task, "project"):
            owner = obj.task.project.owner
        return request.user.is_staff or owner == request.user


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, OwnedOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ActivityLog.objects.create(actor=self.request.user, action="project.created", metadata={"project_id": project.id})


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project__owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        if project.owner != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Cannot create task in project you do not own")
        task = serializer.save()
        ActivityLog.objects.create(actor=self.request.user, action="task.created", metadata={"task_id": task.id})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(task__project__owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        task = serializer.validated_data["task"]
        if task.project.owner != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("Cannot comment on task you do not own")
        comment = serializer.save(author=self.request.user)
        ActivityLog.objects.create(actor=self.request.user, action="comment.created", metadata={"comment_id": comment.id})


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.filter(actor=self.request.user).order_by("-created_at")
