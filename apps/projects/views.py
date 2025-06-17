from typing import Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.forms.project import (
    ProjectForm,
)
from apps.projects.models import Project, ProjectMember, ProjectStatus
from apps.tasks.models import TaskTimeLog
from config.typess import AuthenticatedHttpRequest, AuthenticatedRequest


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


class ProjectView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "projects/project.html"
    extra_context = None

    def get_object(self) -> Project:
        return get_object_or_404(
            Project.objects.filter(
                members__user=cast(AuthenticatedHttpRequest, self.request).user,
            ),
            id=self.kwargs["project_id"],
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context["project"] = project
        total_hours = (
            TaskTimeLog.objects.filter(task__project=project).aggregate(
                models.Sum("hours"),
            )["hours__sum"]
            or 0
        )
        context["total_hours"] = f"{total_hours:.2f}"
        return context


class ProjectUView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get", "post"]
    template_name = "projects/edit_project.html"
    extra_context = None

    def get_object(self) -> Project:
        return get_object_or_404(
            Project,
            owner_id=cast(AuthenticatedHttpRequest, self.request).user.id,
            id=self.kwargs["project_id"],
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not context.get("project"):
            project = self.get_object()
            context["project"] = project
        if not context.get("form"):
            form = ProjectForm(instance=context["project"])
            context["form"] = form
        return context

    def post(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        project = self.get_object()
        form = ProjectForm(request.POST, instance=project)
        if not form.is_valid():
            return self.get(
                request,
                *args,
                **kwargs,
                project=project,
                form=form,
            )

        status_names = request.POST.getlist("status_names[]")
        member_ids = set(int(id_) for id_ in request.POST.getlist("member_ids[]"))
        statuses_map = {name: i for i, name in enumerate(status_names)}
        free_statuses: list[ProjectStatus] = []
        with transaction.atomic():
            for status in project.statuses.all():
                if status.name not in status_names:
                    free_statuses.append(status)
                else:
                    status.position = statuses_map.pop(status.name)
                    status.save()
            for name, position in statuses_map.items():
                if free_statuses:
                    status = free_statuses.pop()
                else:
                    status = ProjectStatus(project=project)
                status.name = name
                status.position = position
                status.save()
            for status in free_statuses:
                status.delete()

            for member in project.members.all():
                if member.user_id == project.owner_id:
                    continue
                if member.id not in member_ids:
                    member.delete()

            form.save()
        return redirect("projects:project", project_id=project.id)
