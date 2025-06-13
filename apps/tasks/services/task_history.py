from decimal import Decimal
from typing import TypedDict

from apps.tasks.models import (
    Task,
    TaskComment,
    TaskHistoryEntry,
    TaskTimeLog,
)
from apps.users.models import User


class TaskOldValues(TypedDict):
    title: str
    description: str
    status_id: int | None
    executor_id: int | None
    project_id: int
    parent_id: int | None


class TimeLogOldValues(TypedDict):
    hours: Decimal
    description: str | None


class TaskCommentOldValues(TypedDict):
    text: str


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
        return self.task.history.create(
            text=f"Added time log #{timelog.id}: {timelog.hours}h"
            + (" and description" if timelog.description else ""),
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
            changes.append(f"from {old_values['hours']} to {timelog.hours}hh")
        if old_values["description"] != timelog.description:
            changes.append("description updated")
        if not changes:
            return None
        return self.task.history.create(
            text=f"Updated time log #{timelog.id}: {', '.join(changes)}",
            created_at=timelog.updated_at,
            user=self.user,
            task=self.task,
        )

    def delete_timelog(self, timelog: TaskTimeLog) -> TaskHistoryEntry:
        return self.task.history.create(
            text=f"Deleted time log #{timelog.id}: {timelog.hours}h",
            created_at=timelog.created_at,
            user=self.user,
            task=self.task,
        )

    def add_comment(self, comment: TaskComment) -> TaskHistoryEntry:
        return self.task.history.create(
            text=f"Left comment #{comment.id}",
            created_at=comment.created_at,
            user=self.user,
            task=self.task,
        )

    def update_comment(
        self,
        comment: TaskComment,
        old_values: TaskCommentOldValues,
    ) -> TaskHistoryEntry | None:
        if old_values["text"] == comment.text:
            return None
        return self.task.history.create(
            text=f"Updated comment #{comment.id}",
            created_at=comment.updated_at,
            user=self.user,
            task=self.task,
        )

    def delete_comment(self, comment: TaskComment) -> TaskHistoryEntry:
        return self.task.history.create(
            text=f"Deleted comment #{comment.id}",
            created_at=comment.created_at,
            user=self.user,
            task=self.task,
        )
