from django import forms

from apps.projects.models import Project
from apps.users.models import User

from ..models import Task, TaskComment, TaskLogTime


class CTaskForm(forms.ModelForm[Task]):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "executor", "project"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "id": "title",
                    "class": "w-1/2 rounded rounded border border-gray-300 p-1",
                    "placeholder": "Enter title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "description",
                    "class": "w-2/3 resize rounded border border-gray-300 p-1",
                    "placeholder": "Enter description",
                    "rows": 12,
                }
            ),
            "status": forms.Select(
                attrs={
                    "id": "status",
                    "class": "rounded border border-gray-300 p-1",
                }
            ),
            "project": forms.Select(
                attrs={
                    "id": "project",
                    "class": "rounded border border-gray-300 p-1",
                }
            ),
            "executor": forms.Select(
                attrs={
                    "id": "executor",
                    "class": "rounded border border-gray-300 p-1",
                    "disabled": True,
                }
            ),
        }


class UTaskForm(forms.ModelForm[Task]):
    executor: forms.ModelChoiceField[User]
    project: forms.ModelChoiceField[Project]

    class Meta:
        model = Task
        fields = ["title", "description", "status", "executor", "project"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "id": "title",
                    "class": "w-1/2 rounded rounded border border-gray-300 p-1",
                    "placeholder": "Enter title",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "description",
                    "class": "w-2/3 resize rounded border border-gray-300 p-1",
                    "placeholder": "Enter description",
                    "rows": 12,
                }
            ),
            "status": forms.Select(
                attrs={
                    "id": "status",
                    "class": "rounded border border-gray-300 p-1",
                }
            ),
            "project": forms.Select(
                attrs={
                    "id": "project",
                    "class": "rounded border border-gray-300 p-1",
                }
            ),
            "executor": forms.Select(
                attrs={
                    "id": "executor",
                    "class": "rounded border border-gray-300 p-1",
                }
            ),
        }


class CTaskCommentForm(forms.ModelForm[TaskComment]):
    class Meta:
        model = TaskComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "id": "comment",
                    "class": "w-2/3 resize rounded border border-gray-300 p-1",
                    "placeholder": "Enter comment",
                    "rows": 4,
                }
            ),
        }


class CTaskLogTimeForm(forms.ModelForm[TaskLogTime]):
    class Meta:
        model = TaskLogTime
        fields = ["description", "hours"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "id": "comment",
                    "class": "w-2/3 resize rounded border border-gray-300 p-1",
                    "placeholder": "Enter comment",
                    "rows": 2,
                }
            ),
            "hours": forms.NumberInput(
                attrs={
                    "id": "hours",
                    "class": "w-[80px] rounded rounded border border-gray-300 p-1",
                    "placeholder": "000.00",
                }
            ),
        }
