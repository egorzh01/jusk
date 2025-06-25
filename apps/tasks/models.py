from typing import TYPE_CHECKING, Any

from django.core.validators import MinValueValidator
from django.db import connection, models
from django_stubs_ext.db.models import TypedModelMeta

if TYPE_CHECKING:
    pass


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
    title = models.CharField(
        max_length=128,
    )
    last_comment_number = models.PositiveIntegerField(
        default=0,
    )
    last_timelog_number = models.PositiveIntegerField(
        default=0,
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
    status = models.ForeignKey(
        "projects.ProjectStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.title

    def display_status(self) -> str:
        if not self.status:
            return "No status"
        return self.status.name

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.descendant_ids: list[int] | None = None

    def get_all_descendant_ids(self) -> list[int]:
        if self.descendant_ids is not None:
            return self.descendant_ids
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    WITH RECURSIVE task_descendants AS (
                        SELECT id
                        FROM tasks
                        WHERE parent_id = %s
                        UNION ALL
                        SELECT t.id
                        FROM tasks t
                        INNER JOIN task_descendants td ON td.id = t.parent_id
                    )
                    SELECT * FROM task_descendants;
                    """,
                [self.id],
            )
            result = cursor.fetchall()
        self.descendant_ids = [row[0] for row in result]
        return self.descendant_ids

    class Meta(TypedModelMeta):
        db_table = "tasks"
        verbose_name = "task"
        verbose_name_plural = "tasks"
        ordering = ["-updated_at"]


class TaskComment(WithCreatedAtAndUpdatedAt):
    number = models.PositiveIntegerField(
        editable=False,
    )
    text = models.TextField()
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="comments",
        editable=False,
    )

    class Meta(TypedModelMeta):
        db_table = "task_comments"
        verbose_name = "task comment"
        verbose_name_plural = "task comments"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "number"],
                name="task_comment__task_number_unique",
            ),
        ]


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
    number = models.PositiveIntegerField(
        editable=False,
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="timelogs",
        editable=False,
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="timelogs",
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
        db_table = "task_timelogs"
        verbose_name = "time log"
        verbose_name_plural = "time logs"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "number"],
                name="task_timelog__task_number_unique",
            ),
        ]
