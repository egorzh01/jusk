from decimal import Decimal
from typing import TypedDict

from apps.tasks.models import Task, TaskComment, TaskHistoryEntry, TaskTimeLog
from apps.users.models import User


class TimeLogOldValues(TypedDict):
    hours: Decimal
    description: str | None


class TaskHistoryService:
    def __init__(
        self,
        task: Task,
        user: User,
    ) -> None:
        self.task = task
        self.user = user

    def create(self) -> None:
        self.task.history.create(
            text=f"Task #{self.task.id} created",
            created_at=self.task.created_at,
            user=self.user,
        )

    def update(self) -> None:
        self.task.history.create(
            text=f"Task #{self.task.id} updated",
            created_at=self.task.updated_at,
            user=self.user,
        )

    def add_timelog(
        self,
        timelog: TaskTimeLog,
    ) -> TaskHistoryEntry:
        if timelog.description:
            pass
        return self.task.history.create(
            text=f"Added time log: {timelog.hours}h, {timelog.description}",
            created_at=timelog.created_at,
            user=self.user,
            task=self.task,
        )

    def update_timelog(
        self,
        timelog: TaskTimeLog,
        old_values: TimeLogOldValues,
    ) -> TaskHistoryEntry | None:
        changes = []
        if old_values["hours"] != timelog.hours:
            changes.append(f"Hours: {old_values['hours']} -> {timelog.hours}")
        if old_values["description"] != timelog.description:
            changes.append(f"Description: {timelog.description}")
        if not changes:
            return None
        return self.task.history.create(
            text=f"Updated time log: {', '.join(changes)}",
            created_at=timelog.updated_at,
            user=self.user,
            task=self.task,
        )

    def delete_timelog(self, timelog: TaskTimeLog) -> TaskHistoryEntry:
        return self.task.history.create(
            text=f"Deleted time log: {timelog.hours}h - {timelog.description}",
            created_at=timelog.created_at,
            user=self.user,
            task=self.task,
        )

    def add_comment(self, comment: TaskComment) -> TaskHistoryEntry:
        return self.task.history.create(
            text=f"Added comment: {comment.text}",
            created_at=comment.created_at,
            user=self.user,
            task=self.task,
        )

    def update_comment(
        self,
        comment: TaskComment,
        old_comment: TaskComment,
    ) -> TaskHistoryEntry | None:
        changes = []
        if old_comment.text != comment.text:
            changes.append(f"{comment.text}")
        return self.task.history.create(
            text=f"Updated comment: {', '.join(changes)}",
            created_at=comment.updated_at,
            user=self.user,
            task=self.task,
        )

    def delete_comment(self, comment: TaskComment) -> TaskHistoryEntry:
        return self.task.history.create(
            text=f"Deleted comment: {comment.text}",
            created_at=comment.created_at,
            user=self.user,
            task=self.task,
        )
