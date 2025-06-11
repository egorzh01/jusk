# urls.py
from django.urls import path

from apps.projects.views import ProjectSelectsAPIView

app_name = "projects"

urlpatterns = [
    path(
        "<int:project_id>/selects/",
        ProjectSelectsAPIView.as_view(),
        name="project_members",
    ),
]
