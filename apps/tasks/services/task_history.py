from datetime import datetime

from apps.tasks.models import Task
from apps.users.models import User


class TaskHistoryService:
    def __init__(self, task: Task, user: User) -> None:
        self.task = task
        self.user = user

    def add_create_history(self, task_created_at: datetime) -> None:
        self.task.history.create(
            text=f"Task #{self.task.id} created",
            created_at=task_created_at,
            user=self.user,
        )

    def add_update_history(self) -> None:
        self.task.history.create(text=f"Task #{self.task.id} updated")
