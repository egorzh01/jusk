from django.urls import path

from apps.tasks.views import CTaskView, TaskView, TimeLogAPIView, UTaskView

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
        TimeLogAPIView.as_view(),
        name="timelog_detail",
    ),
]
