from django.db import models
from django_stubs_ext.db.models import TypedModelMeta


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
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.title

    class Meta(TypedModelMeta):
        db_table = "projects"
        verbose_name = "project"
        verbose_name_plural = "projects"


class ProjectMember(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="members",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="projects",
    )

    def __str__(self) -> str:
        return f"{self.project} - {self.user}"

    class Meta(TypedModelMeta):
        db_table = "project_members"
        verbose_name = "project member"
        verbose_name_plural = "project members"
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_member",
            ),
        ]


class ProjectStatus(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="statuses",
    )
    name = models.CharField(
        max_length=32,
    )
    position = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta(TypedModelMeta):
        db_table = "project_statuses"
        verbose_name = "project status"
        verbose_name_plural = "project statuses"
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="unique_project_name",
            ),
        ]


class ProjectJoinRequest(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        editable=False,
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        editable=False,
    )
    message = models.TextField(
        max_length=256,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )

    class Meta(TypedModelMeta):
        db_table = "project_join_requests"
        verbose_name = "project join request"
        verbose_name_plural = "project join requests"
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "user"],
                name="unique_project_join_request",
            ),
        ]
