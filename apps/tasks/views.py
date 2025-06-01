from typing import Any, cast

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from apps.projects.models import Project
from apps.tasks.forms.task import (
    CTaskCommentForm,
    CTaskForm,
    CTaskLogTimeForm,
    UTaskForm,
)
from apps.tasks.models import Task
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
            members__user=cast(User, self.request.user)
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

        return super().get(request, *args, **kwargs)


class TaskView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/task.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["task"] = get_object_or_404(Task, pk=self.kwargs["task_id"])
        return context


class UTaskView(LoginRequiredMixin, TemplateView):
    http_method_names = ["get"]
    template_name = "tasks/edit_task.html"
    extra_context = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        task = Task.objects.get(pk=self.kwargs["task_id"])
        context["task"] = task
        form = UTaskForm(instance=context["task"])
        executor_field = cast(forms.ModelChoiceField[User], form.fields["executor"])
        executor_field.queryset = User.objects.filter(project=task.project)
        project_field = cast(forms.ModelChoiceField[Project], form.fields["project"])
        project_field.queryset = Project.objects.filter(
            members__user=cast(User, self.request.user)
        )
        context["form"] = form
        context["comment_form"] = CTaskCommentForm()
        context["log_time_form"] = CTaskLogTimeForm()

        return context

    def post(
        self,
        request: AuthenticatedHttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])

        task_form = UTaskForm(request.POST, instance=task)
        comment_form = CTaskCommentForm(
            request.POST,
            initial={
                "task": task,
                "creator": request.user,
            },
        )
        log_time_form = CTaskLogTimeForm(
            request.POST,
            initial={
                "task": task,
                "creator": request.user,
            },
        )
        if (
            task_form.is_valid()
            and comment_form.is_valid()
            and log_time_form.is_valid()
        ):
            task_form.save()
            comment_text = comment_form.cleaned_data.get("text")
            if comment_text:
                comment = comment_form.save(commit=False)
                comment.task = task
                comment.creator = request.user
                comment.save()  #TODO Закончил здесь
            return redirect("task_detail", pk=task.pk)

        return redirect("tasks:task", task_id=self.kwargs["task_id"])
