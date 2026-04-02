from rest_framework.routers import DefaultRouter

from .views import ActivityLogViewSet, CommentViewSet, ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")
router.register("comments", CommentViewSet, basename="comment")
router.register("activity", ActivityLogViewSet, basename="activity")

urlpatterns = router.urls
