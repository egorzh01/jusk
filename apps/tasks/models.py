from typing import TYPE_CHECKING

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

if TYPE_CHECKING:
    pass


class TaskStatus(models.TextChoices):
    NEW = "NEW", _("New")
    IN_PROGRESS = "IN_PROGRESS", _("In progress")
    DONE = "DONE", _("Done")
    CANCELED = "CANCELED", _("Canceled")


class WithCreatedAtAndUpdatedAt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def was_updated(self) -> bool:
        return self.updated_at.replace(microsecond=0) > self.created_at.replace(
            microsecond=0,
        )

    class Meta:
        abstract = True


class Task(WithCreatedAtAndUpdatedAt):
    status = models.CharField(
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
    )
    title = models.CharField(
        max_length=128,
    )
    description = models.TextField()
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

    class Meta(TypedModelMeta):
        db_table = "tasks"
        verbose_name = "task"
        verbose_name_plural = "tasks"
        ordering = ["-updated_at"]


class TaskComment(WithCreatedAtAndUpdatedAt):
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="comments",
        editable=False,
    )
    text = models.TextField()
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
    )

    class Meta(TypedModelMeta):
        db_table = "task_comments"
        verbose_name = "task comment"
        verbose_name_plural = "task comments"
        ordering = ["-created_at"]


class TaskHistoryEntry(models.Model):
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="history",
        editable=False,
    )
    text = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
    )

    class Meta(TypedModelMeta):
        db_table = "task_history"
        verbose_name = "task history entry"
        verbose_name_plural = "task history entries"
        ordering = ["-created_at"]


class TaskTimeLog(WithCreatedAtAndUpdatedAt):
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="time_logs",
        editable=False,
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="time_logs",
        editable=False,
    )
    hours = models.DecimalField(
        max_digits=5,  # до 999.99 часов
        decimal_places=2,
        help_text="Количество часов, потраченных на задачу",
        validators=[MinValueValidator(0)],
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Описание выполненной работы (необязательно)",
    )

    class Meta(TypedModelMeta):
        db_table = "task_time_logs"
        verbose_name = "time log"
        verbose_name_plural = "time logs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.creator} — {self.task} — {self.hours} ч."
