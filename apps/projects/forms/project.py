from django import forms

from apps.projects.models import Project


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
