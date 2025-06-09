from typing import Any, cast

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.views import APIView

from apps.projects.models import Project
from apps.tasks.forms.task import (
    CTaskForm,
    UTaskForm,
)
from apps.tasks.models import Task, TaskComment, TaskTimeLog
from apps.tasks.services.task_history import TaskHistoryService
from apps.users.models import User
from config.typess import AuthenticatedHttpRequest


class HomeView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/home.html"
    extra_context = None

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["tasks"] = Task.objects.filter(executor=cast(User, self.request.user))
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
            form = CTaskForm()
            executor_field = cast(forms.ModelChoiceField[User], form.fields["executor"])
            executor_field.queryset = User.objects.none()
            project_field = cast(
                forms.ModelChoiceField[Project],
                form.fields["project"],
            )
            project_field.queryset = Project.objects.filter(
                members__user=cast(User, self.request.user),
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
        with transaction.atomic():
            task = form.save()
            history_service = TaskHistoryService(
                task=task,
                user=request.user,
            )
            history_service.add_create_history(
                task_created_at=task.created_at,
            )

        return redirect("tasks:task", task_id=task.id)


class TaskView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/task.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        context["task"] = task
        total_hours = (
            TaskTimeLog.objects.filter(task=task).aggregate(Sum("hours"))["hours__sum"]
            or 0
        )
        context["total_hours"] = f"{total_hours:.2f}"
        return context


class UTaskView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get", "post"]
    template_name = "tasks/edit_task.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        task = Task.objects.get(pk=self.kwargs["task_id"])
        context["task"] = task
        if not context.get("form"):
            form = UTaskForm(instance=context["task"])
            executor_field = cast(forms.ModelChoiceField[User], form.fields["executor"])
            executor_field.queryset = User.objects.filter(project=task.project)
            project_field = cast(
                forms.ModelChoiceField[Project],
                form.fields["project"],
            )
            project_field.queryset = Project.objects.filter(
                members__user=cast(User, self.request.user),
            )
            context["form"] = form

        return context

    def post(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])

        form = UTaskForm(
            request.POST,
            instance=task,
        )

        if not form.is_valid():
            return super().get(request, *args, **kwargs, form=form)
        with transaction.atomic():
            comment_text = form.cleaned_data.get("comment_text")
            if comment_text:
                TaskComment.objects.create(
                    task=task,
                    creator=request.user,
                    text=comment_text,
                )

            log_description = form.cleaned_data.get("log_description")
            log_hours = form.cleaned_data.get("log_hours")
            print(type(log_description), log_hours)
            if log_hours:
                TaskTimeLog.objects.create(
                    task=task,
                    creator=request.user,
                    description=log_description,
                    hours=log_hours,
                )
            if log_hours or log_description or form.has_changed():
                form.save()

        return redirect("tasks:task", task_id=task.id)


class TimeLogAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(TimeLog, pk=pk, creator=user)

    def patch(self, request, pk):
        time_log = self.get_object(pk, request.user)
        serializer = TimeLogSerializer(time_log, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # запись в историю
            History.objects.create(
                user=request.user,
                task=time_log.task,
                text=f"Updated time log: {time_log.hours}h - {time_log.description}"
            )
            
            return Response({
                'timelog': serializer.data,
                'history_entry': {
                    'user': str(request.user),
                    'created_at': timezone.now().strftime("%Y-%m-%d %H:%M"),
                    'text': f"Updated time log: {time_log.hours}h - {time_log.description}"
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        time_log = self.get_object(pk, request.user)
        time_log.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
