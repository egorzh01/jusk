from typing import Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.forms.project import (
    ProjectForm,
)
from apps.projects.models import (
    Project,
    ProjectJoinRequest,
    ProjectMember,
    ProjectStatus,
)
from apps.tasks.models import TaskTimeLog
from config.typess import AuthenticatedHttpRequest, AuthenticatedRequest


class ProjectSelectionView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "projects/project_selection.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["projects"] = Project.objects.filter(
            members__user=cast(AuthenticatedHttpRequest, self.request).user
        )
        return ctx


class ProjectSelectionRedirectView(LoginRequiredMixin, View):
    http_method_names = ["get"]

    def get(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        project_id = kwargs["project_id"]
        project = get_object_or_404(
            Project.objects.filter(
                members__user=cast(AuthenticatedHttpRequest, self.request).user
            ),
            id=project_id,
        )

        if next_url_name := request.GET.get("next"):
            url = reverse(next_url_name, kwargs={"project_id": project.id})
            return redirect(url)

        return redirect("projects:project", project_id=project.id)


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
        project = get_object_or_404(
            Project,
            id=self.kwargs["project_id"],
        )
        if project.owner_id != self.request.user.id:
            raise PermissionDenied
        return project

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

        unique_statuses = {
            name[:32]: int(id_) if id_ else -1
            for id_, name in zip(
                request.POST.getlist("status_ids[]"),
                request.POST.getlist("status_names[]"),
                strict=True,
            )
        }
        existing_statuses = {s.id: s for s in project.statuses.all()}
        member_ids = {int(id_) for id_ in request.POST.getlist("member_ids[]")}

        with transaction.atomic():
            # Обновление/создание статусов
            for position, (name, status_id) in enumerate(unique_statuses.items()):
                if status := existing_statuses.pop(status_id, None):
                    status.name = name
                    status.position = position
                    status.save()
                else:
                    ProjectStatus.objects.create(
                        project=project,
                        name=name,
                        position=position,
                    )

            ProjectStatus.objects.filter(id__in=existing_statuses.keys()).delete()

            project.members.exclude(user_id=project.owner_id).exclude(
                id__in=member_ids,
            ).delete()

        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project", project_id=project.id)
        return self.get(request, *args, **kwargs, project=project, form=form)


class ProjectJoinRequestAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "delete"]

    def get_object(self) -> ProjectJoinRequest:
        pjr = get_object_or_404(
            ProjectJoinRequest,
            id=self.kwargs["join_request_id"],
            project_id=self.kwargs["project_id"],
        )
        if pjr.project.owner_id != self.request.user.id:
            raise PermissionDenied
        return pjr

    def patch(
        self,
        request: AuthenticatedRequest,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        pjr = self.get_object()
        member = ProjectMember.objects.filter(
            project=pjr.project,
            user=pjr.user,
        ).first()
        if member:
            pjr.delete()
            return Response()
        with transaction.atomic():
            ProjectMember.objects.create(
                project=pjr.project,
                user=pjr.user,
            )
            pjr.delete()
        return Response(
            data={
                "member": {
                    "id": pjr.user.id,
                    "name": str(pjr.user),
                },
            },
        )

    def delete(
        self,
        request: AuthenticatedRequest,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        pjr = self.get_object()
        pjr.delete()
        return Response(status=204)
