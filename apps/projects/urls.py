# urls.py
from django.urls import path

from apps.projects.views import (
    ProjectJoinRequestAPIView,
    ProjectSelectionRedirectView,
    ProjectSelectionView,
    ProjectUView,
    ProjectView,
)

app_name = "projects"

urlpatterns = [
    path(
        "select",
        ProjectSelectionView.as_view(),
        name="selection",
    ),
    path(
        "select/<int:project_id>/redirect/",
        ProjectSelectionRedirectView.as_view(),
        name="project_selection_redirect",
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
    path(
        "api/projects/<int:project_id>/join_requests/<int:join_request_id>/",
        ProjectJoinRequestAPIView.as_view(),
        name="join_request_detail",
    ),
]
