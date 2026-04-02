from django.contrib import admin

from .models import ActivityLog, Comment, Project, Task

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(ActivityLog)
