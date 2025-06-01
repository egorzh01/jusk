from django.http import JsonResponse

from config.typess import AuthenticatedHttpRequest

from .models import ProjectMember


def project_members(
    request: AuthenticatedHttpRequest,
    project_id: int,
) -> JsonResponse:
    members = ProjectMember.objects.filter(project_id=project_id).select_related("user")

    data = {
        "members": [
            {
                "id": member.user.id,
                "name": str(member.user),
            }
            for member in members
        ]
    }
    return JsonResponse(data)
