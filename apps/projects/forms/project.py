from typing import Any

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.projects.models import Project, ProjectMember, ProjectStatus


class ProjectForm(forms.ModelForm[Project]):
    class Meta:
        model = Project
        fields = ["title", "description"]
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
        }


class BaseProjectFormSet(BaseInlineFormSet[Any, Any, Any]):
    def add_fields(
        self,
        form: Any,
        index: int | None,
    ) -> None:
        super().add_fields(form, index)
        form.fields["DELETE"].widget = forms.HiddenInput()


ProjectMemberFormSet: type[BaseInlineFormSet[ProjectMember, Project, Any]] = (
    inlineformset_factory(
        parent_model=Project,
        model=ProjectMember,
        fields=["user"],
        extra=0,
        can_delete=True,
        formset=BaseProjectFormSet,
        widgets={
            "user": forms.Select(attrs={"class": "border rounded p-1 w-full"}),
        },
    )
)

ProjectStatusFormSet: type[BaseInlineFormSet[ProjectStatus, Project, Any]] = (
    inlineformset_factory(
        parent_model=Project,
        model=ProjectStatus,
        fields=["name", "position"],
        extra=0,
        can_delete=True,
        formset=BaseProjectFormSet,
        widgets={
            "name": forms.TextInput(attrs={"class": "border rounded p-1 w-full"}),
        },
    )
)
