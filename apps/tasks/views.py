from typing import Any, cast

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project, ProjectStatus
from apps.tasks.forms.task import (
    CTaskForm,
    UTaskForm,
)
from apps.tasks.models import Task, TaskComment, TaskTimeLog
from apps.tasks.serializers import CommentSerializer, TimeLogSerializer
from apps.tasks.services.task_checker import TaskChecker
from apps.tasks.services.task_history import (
    TaskCommentOldValues,
    TaskHistoryService,
    TaskOldValues,
    TimeLogOldValues,
)
from apps.users.models import User
from config.typess import AuthenticatedHttpRequest, AuthenticatedRequest


class HomeView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/home.html"
    extra_context = None

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(
            executor=cast(User, self.request.user)
        ).only("id", "title", "status", "updated_at")
        context["projects"] = Project.objects.filter(
            members__user=cast(User, self.request.user)
        ).only("id", "title")
        return context


class CTaskView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get", "post"]
    template_name = "tasks/create_task.html"
    extra_context = None

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not context.get("form"):
            context["project"] = get_object_or_404(
                Project.objects.filter(members__user=cast(User, self.request.user)),
                id=self.kwargs["project_id"],
            )
            form = CTaskForm()
            executor_field = cast(forms.ModelChoiceField[User], form.fields["executor"])
            executor_field.queryset = User.objects.filter(
                projects__project=context["project"],
            )
            context["form"] = form
        return context

    def post(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        form = CTaskForm(request.POST)
        if not form.is_valid():
            return super().get(request, *args, **kwargs, form=form)
        form.instance.creator = request.user
        TaskChecker.check_all(
            status_id=form.instance.status_id,
            project=form.instance.project,
            user=request.user,
            executor=form.instance.executor,
        )
        with transaction.atomic():
            task = form.save()
            history_service = TaskHistoryService(
                task=task,
                user=request.user,
            )
            history_service.create()

        return redirect("tasks:task", task_id=task.id)


class TaskView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/task.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        task = get_object_or_404(
            Task.objects.filter(
                project__members__user=cast(AuthenticatedHttpRequest, self.request).user
            ),
            id=self.kwargs["task_id"],
        )
        context["task"] = task
        total_hours = (
            TaskTimeLog.objects.filter(task=task).aggregate(models.Sum("hours"))[
                "hours__sum"
            ]
            or 0
        )
        context["total_hours"] = f"{total_hours:.2f}"
        return context


class TaskUView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get", "post"]
    template_name = "tasks/edit_task.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not context.get("task"):
            task = get_object_or_404(
                Task.objects.filter(
                    project__members__user=cast(
                        AuthenticatedHttpRequest, self.request
                    ).user
                ),
                id=self.kwargs["task_id"],
            )
            context["task"] = task
        if not context.get("form"):
            form = UTaskForm(instance=context["task"])
            executor_field = cast(forms.ModelChoiceField[User], form.fields["executor"])
            executor_field.queryset = User.objects.filter(
                projects__project=task.project
            )
            project_field = cast(
                forms.ModelChoiceField[Project], form.fields["project"]
            )
            project_field.queryset = Project.objects.filter(
                members__user=cast(User, self.request.user),
            )
            status_field = cast(
                forms.ModelChoiceField[ProjectStatus], form.fields["status"]
            )
            statuses_qs = ProjectStatus.objects.filter(project=task.project)
            if statuses_qs.exists():
                status_field.empty_label = None
            else:
                status_field.queryset = ProjectStatus.objects.none()
            context["form"] = form

        return context

    def post(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        task = get_object_or_404(
            Task.objects.filter(
                project__members__user=cast(AuthenticatedHttpRequest, self.request).user
            ),
            id=self.kwargs["task_id"],
        )
        old_values = TaskOldValues(
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            executor_id=task.executor_id,
            status_id=task.status_id,
            parent_id=task.parent_id,
        )
        form = UTaskForm(
            request.POST,
            instance=task,
        )

        if not form.is_valid():
            return super().get(
                request,
                *args,
                **kwargs,
                form=form,
                task=task,
            )
        TaskChecker.check_all(
            status_id=form.instance.status_id,
            project=form.instance.project,
            user=request.user,
            executor=form.instance.executor,
            old_values=old_values,
        )
        history_service = TaskHistoryService(
            task=task,
            user=request.user,
        )
        with transaction.atomic():
            comment_text = form.cleaned_data.get("comment_text")
            if comment_text:
                task.last_comment_number += 1
                comment = TaskComment.objects.create(
                    task=task,
                    number=task.last_comment_number,
                    creator=request.user,
                    text=comment_text,
                )
                history_service.add_comment(comment)

            log_description = form.cleaned_data.get("log_description")
            log_hours = form.cleaned_data.get("log_hours")
            if log_hours:
                task.last_timelog_number += 1
                timelog = TaskTimeLog.objects.create(
                    task=task,
                    number=task.last_timelog_number,
                    creator=request.user,
                    description=log_description,
                    hours=log_hours,
                )
                history_service.add_timelog(timelog)
            if form.has_changed():
                history_service.update()
            task.save()
        return redirect("tasks:task", task_id=task.id)


class TaskTimeLogAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "delete"]

    def patch(
        self,
        request: AuthenticatedRequest,
        task_id: int,
        timelog_id: int,
    ) -> Response:
        timelog = get_object_or_404(
            TaskTimeLog,
            id=timelog_id,
            creator=request.user,
            task_id=task_id,
        )
        old_values = TimeLogOldValues(
            hours=timelog.hours,
            description=timelog.description,
        )
        serializer = TimeLogSerializer(
            timelog,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            serializer.save()

            history_service = TaskHistoryService(
                task=timelog.task,
                user=request.user,
            )
            history_entry = history_service.update_timelog(
                timelog=timelog,
                old_values=old_values,
            )
        total_hours = (
            TaskTimeLog.objects.filter(task=timelog.task).aggregate(
                models.Sum("hours")
            )["hours__sum"]
            or 0
        )
        return Response(
            data={
                "timelog": serializer.data,
                "total_hours": f"{total_hours:.2f}",
                "history_entry": {
                    "user": str(request.user),
                    "created_at": history_entry.created_at,
                    "text": history_entry.text,
                }
                if history_entry
                else None,
            },
        )

    def delete(
        self,
        request: AuthenticatedRequest,
        timelog_id: int,
        task_id: int,
    ) -> Response:
        timelog = get_object_or_404(
            TaskTimeLog,
            id=timelog_id,
            creator=request.user,
            task_id=task_id,
        )
        with transaction.atomic():
            timelog.delete()
            history_service = TaskHistoryService(
                task=timelog.task,
                user=request.user,
            )
            history_entry = history_service.delete_timelog(timelog)
        total_hours = (
            TaskTimeLog.objects.filter(task=timelog.task).aggregate(
                models.Sum("hours")
            )["hours__sum"]
            or 0
        )
        return Response(
            data={
                "total_hours": f"{total_hours:.2f}",
                "history_entry": {
                    "user": str(request.user),
                    "created_at": history_entry.created_at,
                    "text": history_entry.text,
                },
            },
        )


class TaskCommentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch", "delete"]

    def patch(
        self,
        request: AuthenticatedRequest,
        task_id: int,
        comment_id: int,
    ) -> Response:
        comment = get_object_or_404(
            TaskComment,
            id=comment_id,
            creator=request.user,
            task_id=task_id,
        )
        old_values = TaskCommentOldValues(
            text=comment.text,
        )
        serializer = CommentSerializer(
            comment,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            serializer.save()

            history_service = TaskHistoryService(
                task=comment.task,
                user=request.user,
            )
            history_entry = history_service.update_comment(
                comment=comment,
                old_values=old_values,
            )
        return Response(
            data={
                "comment": serializer.data,
                "history_entry": {
                    "user": str(request.user),
                    "created_at": history_entry.created_at,
                    "text": history_entry.text,
                }
                if history_entry
                else None,
            },
        )

    def delete(
        self,
        request: AuthenticatedRequest,
        comment_id: int,
        task_id: int,
    ) -> Response:
        comment = get_object_or_404(
            TaskComment,
            id=comment_id,
            creator=request.user,
            task_id=task_id,
        )
        history_service = TaskHistoryService(
            task=comment.task,
            user=request.user,
        )
        with transaction.atomic():
            history_entry = history_service.delete_comment(comment)
            comment.delete()

        return Response(
            data={
                "history_entry": {
                    "user": str(request.user),
                    "created_at": history_entry.created_at,
                    "text": history_entry.text,
                },
            },
        )
