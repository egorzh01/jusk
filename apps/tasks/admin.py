from django.contrib import admin

# Register your models here.
# users/admin.py
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin[Task]):
    ordering = ["created_at", "updated_at", "executor"]
    filter = ("executor",)
    list_display = ["title", "created_at", "updated_at", "executor"]
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
                    "executor",
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

    # обязательно, иначе форма создания суперпользователя не будет работать
    add_form_template = None

    def save_model(
        self,
        request: HttpRequest,
        obj: Task,
        form: ModelForm[Task],
        change: bool,
    ) -> None:
        if not change:
            obj.creator = request.user  # type: ignore

        super().save_model(request, obj, form, change)
