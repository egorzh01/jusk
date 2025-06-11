from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from config.typess import AuthenticatedRequest

from .models import ProjectMember, ProjectStatus


class ProjectSelectsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

    def get(
        self,
        request: AuthenticatedRequest,
        project_id: int,
    ) -> Response:
        get_object_or_404(
            ProjectMember,
            project_id=project_id,
            user=request.user,
        )
        members = ProjectMember.objects.filter(project_id=project_id).select_related(
            "user",
        )
        statuses = ProjectStatus.objects.filter(project_id=project_id)
        return Response(
            data={
                "members": [
                    {
                        "id": member.user.id,
                        "name": str(member.user),
                    }
                    for member in members
                ],
                "statuses": [
                    {
                        "id": status.id,
                        "name": str(status),
                    }
                    for status in statuses
                ],
            },
        )
