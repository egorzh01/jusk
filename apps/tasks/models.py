from django.db import models


class Task(models.Model):
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
        on_delete=models.CASCADE,
        related_name="executed_tasks",
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
        related_name="created_tasks",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "tasks"
        verbose_name = "task"
        verbose_name_plural = "tasks"
