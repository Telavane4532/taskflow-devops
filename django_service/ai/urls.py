from django.urls import path

from .views import ParseTaskView, PrioritizeView, SimilarTasksView, SummarizeView

urlpatterns = [
    path("summarize/", SummarizeView.as_view(), name="ai-summarize"),
    path("prioritize/", PrioritizeView.as_view(), name="ai-prioritize"),
    path("parse-task/", ParseTaskView.as_view(), name="ai-parse-task"),
    path("similar/<int:task_id>/", SimilarTasksView.as_view(), name="ai-similar-tasks"),
]
