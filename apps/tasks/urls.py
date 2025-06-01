from django.urls import path

from apps.tasks.views import CTaskView, TaskView, UTaskView

app_name = "tasks"

urlpatterns = [
    path("new", CTaskView.as_view(), name="new_task"),
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
]
