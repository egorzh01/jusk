# urls.py
from django.urls import path

from apps.projects.views import ProjectSelectsAPIView, ProjectUView, ProjectView

app_name = "projects"

urlpatterns = [
    path(
        "api/<int:project_id>/selects/",
        ProjectSelectsAPIView.as_view(),
        name="project_members",
    ),
    path(
        "<int:project_id>",
        ProjectView.as_view(),
        name="project",
    ),
    path(
        "<int:project_id>/edit",
        ProjectUView.as_view(),
        name="edit_project",
    ),
]
