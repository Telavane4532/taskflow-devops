from rest_framework import serializers

from .models import ActivityLog, Comment, Project, Task


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "owner", "created_at", "updated_at"]
        read_only_fields = ["owner", "created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority_score",
            "ai_summary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["priority_score", "ai_summary", "created_at", "updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "task", "author", "body", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ["id", "actor", "action", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]
