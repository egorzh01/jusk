from django.urls import path

from apps.tasks.views import (
    CTaskView,
    TaskCommentAPIView,
    TaskTimeLogAPIView,
    TaskView,
    UTaskView,
)

app_name = "tasks"

urlpatterns = [
    path(
        "new",
        CTaskView.as_view(),
        name="new_task",
    ),
    path(
        "<int:task_id>",
        TaskView.as_view(),
        name="task",
    ),
    path(
        "<int:task_id>/edit",
        UTaskView.as_view(),
        name="edit_task",
    ),
    path(
        "<int:task_id>/timelogs/<int:timelog_id>/",
        TaskTimeLogAPIView.as_view(),
        name="timelog_detail",
    ),
    path(
        "<int:task_id>/comments/<int:comment_id>/",
        TaskCommentAPIView.as_view(),
        name="comment_detail",
    ),
]
