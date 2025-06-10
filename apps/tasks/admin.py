from typing import cast

from django.contrib import admin
from django.db import transaction

# Register your models here.
# users/admin.py
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.tasks.services.task_history import TaskHistoryService
from apps.users.models import User

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin[Task]):
    ordering = ["created_at", "updated_at"]
    filter = ("executor", "creator", "status")
    list_display = ["id", "project", "title", "status", "executor"]
    search_fields = ["title", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at", "creator"]
    list_filter = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("Info"),
            {
                "fields": (
                    "title",
                    "status",
                    "created_at",
                    "updated_at",
                    "description",
                    "executor",
                    "creator",
                ),
            },
        ),
        (
            _("Relations"),
            {
                "fields": (
                    "project",
                    "next",
                    "previous",
                    "parent",
                ),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "title",
                    "status",
                    "description",
                    "executor",
                    "parent",
                    "next",
                    "previous",
                ),
            },
        ),
    )

    def save_model(
        self,
        request: HttpRequest,
        obj: Task,
        form: ModelForm[Task],
        change: bool,
    ) -> None:
        with transaction.atomic():
            if not change:
                obj.creator = cast(User, request.user)
            super().save_model(request, obj, form, change)

            history_service = TaskHistoryService(
                task=obj,
                user=cast(User, request.user),
            )
            if change:
                history_service.update()
            else:
                history_service.create()
