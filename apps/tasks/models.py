from django.db import models
from django.utils.translation import gettext_lazy as _


class TaskStatus(models.TextChoices):
    NEW = "NEW", _("New")
    IN_PROGRESS = "IN_PROGRESS", _("In progress")
    DONE = "DONE", _("Done")
    CANCELED = "CANCELED", _("Canceled")


class Task(models.Model):
    status = models.CharField(
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
    )
    title = models.CharField(
        max_length=128,
    )
    description = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )
    executor = models.ForeignKey(
        "users.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="executed_tasks",
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
        related_name="created_tasks",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    previous = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    next = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "tasks"
        verbose_name = "task"
        verbose_name_plural = "tasks"
