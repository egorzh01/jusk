from typing import Any

from django import forms

from ..models import Task


class CTaskForm(forms.ModelForm[Task]):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "executor"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "id": "title",
                    "class": "w-1/2 rounded rounded border border-gray-300 p-1",
                    "placeholder": "Enter title",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "description",
                    "class": "w-2/3 resize rounded border border-gray-300 p-1",
                    "placeholder": "Enter description",
                    "rows": 12,
                },
            ),
            "executor": forms.Select(
                attrs={
                    "id": "executor",
                    "class": "rounded border border-gray-300 p-1",
                },
            ),
            "status": forms.Select(
                attrs={
                    "id": "status",
                    "class": "rounded border border-gray-300 p-1",
                },
            ),
        }


class UTaskForm(forms.ModelForm[Task]):
    comment_text = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "id": "comment",
                "class": "w-2/3 resize rounded border border-gray-300 p-1",
                "placeholder": "Enter comment",
                "rows": 4,
            },
        ),
    )
    log_description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "id": "log_description",
                "class": "w-2/3 resize rounded border border-gray-300 p-1",
                "placeholder": "Enter log description",
                "rows": 2,
            },
        ),
    )
    log_hours = forms.DecimalField(
        decimal_places=2,
        max_digits=5,
        min_value=0.0,
        required=False,
        widget=forms.NumberInput(
            attrs={
                "id": "hours",
                "class": "w-[80px] rounded border border-gray-300 p-1",
                "placeholder": "000.00",
            },
        ),
    )

    class Meta:
        model = Task
        fields = ["title", "description", "status", "executor"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "id": "title",
                    "class": "w-1/2 rounded rounded border border-gray-300 p-1",
                    "placeholder": "Enter title",
                },
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "description",
                    "class": "w-2/3 resize rounded border border-gray-300 p-1",
                    "placeholder": "Enter description",
                    "rows": 12,
                },
            ),
            "executor": forms.Select(
                attrs={
                    "id": "executor",
                    "class": "rounded border border-gray-300 p-1",
                },
            ),
            "status": forms.Select(
                attrs={
                    "id": "status",
                    "class": "rounded border border-gray-300 p-1",
                },
            ),
        }

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        assert cleaned_data is not None

        log_description = cleaned_data.get("log_description")
        log_hours = cleaned_data.get("log_hours")
        if log_description and log_hours is None:
            self.add_error(
                "log_hours",
                "This field is required when log time description is filled.",
            )

        return cleaned_data
