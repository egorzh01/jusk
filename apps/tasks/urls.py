from django.urls import path

from apps.tasks.views import (
    CTaskView,
    TaskCommentAPIView,
    TaskTimeLogAPIView,
    TaskUView,
    TaskView,
)

app_name = "tasks"

urlpatterns = [
    path(
        "projects/<int:project_id>/tasks/new",
        CTaskView.as_view(),
        name="new_task",
    ),
    path(
        "tasks/<int:task_id>",
        TaskView.as_view(),
        name="task",
    ),
    path(
        "tasks/<int:task_id>/edit",
        TaskUView.as_view(),
        name="edit_task",
    ),
    path(
        "tasks/<int:task_id>/timelogs/<int:timelog_id>/",
        TaskTimeLogAPIView.as_view(),
        name="timelog_detail",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:comment_id>/",
        TaskCommentAPIView.as_view(),
        name="comment_detail",
    ),
]
