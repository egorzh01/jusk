from django.db import models


class Project(models.Model):
    title = models.CharField(
        max_length=64,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )
    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        db_table = "projects"
        verbose_name = "project"
        verbose_name_plural = "projects"


class ProjectMember(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.project} - {self.user}"

    class Meta:
        db_table = "project_members"
        verbose_name = "project member"
        verbose_name_plural = "project members"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_member",
            ),
        ]
