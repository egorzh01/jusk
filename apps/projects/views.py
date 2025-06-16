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
    ProjectMemberFormSet,
    ProjectStatusFormSet,
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

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(
            Project.objects.filter(
                members__user=cast(AuthenticatedHttpRequest, self.request).user
            ),
            id=self.kwargs["project_id"],
        )
        context["project"] = project
        total_hours = (
            TaskTimeLog.objects.filter(task__project=project).aggregate(
                models.Sum("hours")
            )["hours__sum"]
            or 0
        )
        context["total_hours"] = f"{total_hours:.2f}"
        return context


class ProjectUView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get", "post"]
    template_name = "projects/edit_project.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not context.get("project"):
            project = get_object_or_404(
                Project.objects.filter(
                    members__user=cast(AuthenticatedHttpRequest, self.request).user
                ),
                id=self.kwargs["project_id"],
            )
            context["project"] = project
        if not context.get("form"):
            form = ProjectForm(instance=context["project"])
            status_formset = ProjectStatusFormSet(instance=context["project"])
            member_formset = ProjectMemberFormSet(instance=context["project"])
            context["form"] = form
            context["status_formset"] = status_formset
            context["member_formset"] = member_formset
        return context

    def post(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        project = get_object_or_404(Project, id=kwargs["project_id"])
        form = ProjectForm(request.POST, instance=project)
        status_formset = ProjectStatusFormSet(request.POST, instance=project)
        member_formset = ProjectMemberFormSet(request.POST, instance=project)

        if (
            not form.is_valid()
            or not status_formset.is_valid()
            or not member_formset.is_valid()
        ):
            print(form.errors, status_formset.errors, member_formset.errors)
            return self.get(
                request,
                *args,
                **kwargs,
                project=project,
                form=form,
                status_formset=status_formset,
                member_formset=member_formset,
            )
        with transaction.atomic():
            form.save()
            status_formset.save()
            member_formset.save()
        return redirect("projects:project", project_id=project.id)
