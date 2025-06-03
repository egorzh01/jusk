from typing import Any, cast

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from apps.projects.models import Project
from apps.tasks.forms.task import (
    CTaskForm,
    UTaskForm,
)
from apps.tasks.models import Task, TaskComment, TaskLogTime
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
    template_name = "tasks/new_task.html"
    extra_context = None

    def get_context_data(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form = CTaskForm()
        executor_field = cast(forms.ModelChoiceField[User], form.fields["executor"])
        executor_field.queryset = User.objects.none()
        project_field = cast(forms.ModelChoiceField[Project], form.fields["project"])
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
        if form.is_valid():
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
        context["total_hours"] = (
            TaskLogTime.objects.filter(task=task).aggregate(Sum("hours"))["hours__sum"]
            or 0
        )
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
                forms.ModelChoiceField[Project], form.fields["project"],
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
            if log_description and log_hours:
                TaskLogTime.objects.create(
                    task=task,
                    creator=request.user,
                    description=log_description,
                    hours=log_hours,
                )
            if log_hours or log_description or form.has_changed():
                form.save()

        return redirect("tasks:task", task_id=task.id)
