# urls.py
from django.urls import path

from apps.projects.views import project_members

app_name = "projects"

urlpatterns = [
    path("<int:project_id>/members/", project_members, name="project_members"),
]
