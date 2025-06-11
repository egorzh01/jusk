from typing import cast

from django.contrib import admin

# Register your models here.
# users/admin.py
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.users.models import User

from .models import Project, ProjectMember, ProjectStatus


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin[Project]):
    ordering = ["created_at", "updated_at"]
    filter = ("executor",)
    list_display = ["title", "created_at", "updated_at"]
    search_fields = ["title", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at", "creator"]
    list_filter = ["created_at", "updated_at"]

    fieldsets = (
        (
            _("Info"),
            {
                "fields": (
                    "title",
                    "created_at",
                    "updated_at",
                    "description",
                    "creator",
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
                    "description",
                    "executor",
                ),
            },
        ),
    )

    def save_model(
        self,
        request: HttpRequest,
        obj: Project,
        form: ModelForm[Project],
        change: bool,
    ) -> None:
        if not change:
            obj.creator = cast(User, request.user)

        super().save_model(request, obj, form, change)


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin[ProjectMember]):
    ordering = ["user", "project"]
    filter = (
        "user",
        "project",
    )
    list_display = ["user", "project"]
    search_fields = ["user", "project"]
    list_filter = ["user", "project"]

    fieldsets = (
        (
            _("Info"),
            {
                "fields": ("user", "project"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "project"),
            },
        ),
    )


@admin.register(ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin[ProjectStatus]):
    ordering = ["status", "project"]
    filter = (
        "status",
        "project",
    )
    list_display = ["status", "project"]
    search_fields = ["status", "project"]
    list_filter = ["status", "project"]

    fieldsets = (
        (
            _("Info"),
            {
                "fields": ("status", "project"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("status", "project"),
            },
        ),
    )
