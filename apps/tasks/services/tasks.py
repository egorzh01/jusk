from apps.projects.models import Project
from apps.tasks.services.task_history import TaskOldValues
from apps.users.models import User


def check_task(
    status: str,
    project: Project,
    user: User,
    executor: User | None,
    old_values: TaskOldValues | None = None,
) -> bool:
    if old_values:
        if (
            old_values["project_id"] != project.id
            and not project.members.filter(user=user).exists()
        ):
            return False
        if (
            executor
            and old_values["executor_id"] != executor.id
            and not project.members.filter(user=executor).exists()
        ):
            return False
        return not (
            old_values["status"] != status
            and not project.statuses.filter(status=status).exists()
        )
    return (
        project.members.filter(user=user).exists()
        and project.members.filter(user=executor).exists()
        and project.statuses.filter(status=status).exists()
    )
