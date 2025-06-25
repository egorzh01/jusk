from django.db import connection
from django.forms import ValidationError

from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tasks.services.task_history import TaskOldValues
from apps.users.models import User


class TaskChecker:
    @staticmethod
    def check_all(
        status_id: int | None,
        project: Project,
        user: User,
        executor: User | None,
        old_values: TaskOldValues | None = None,
    ) -> None:
        try:
            if old_values:
                # Проверка на изменение проекта и наличие пользователя в новом проекте
                if old_values["project_id"] != project.id:
                    assert project.members.filter(user=user).exists()

                # Проверка на изменение исполнителя и его участие в проекте
                if executor and old_values["executor_id"] != executor.id:
                    assert project.members.filter(user=executor).exists()

                # Проверка на изменение статуса
                if old_values["status_id"] != status_id:
                    if status_id:
                        assert project.statuses.filter(id=status_id).exists()
                    else:
                        assert not project.statuses.exists()
            else:
                # Пользователь должен быть участником проекта
                assert project.members.filter(user=user).exists()
                # Исполнитель тоже должен быть участником проекта
                assert (
                    executor is None or project.members.filter(user=executor).exists()
                )
                # Статус должен существовать в проекте (или быть пустым, если у проекта нет статусов)
                if status_id:
                    assert project.statuses.filter(id=status_id).exists()
                else:
                    assert not project.statuses.exists()
        except AssertionError as exc:
            raise ValidationError("The changes you made are not allowed") from exc

    @staticmethod
    def get_all_descendants(task: Task) -> list[int]:
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
                [task.id],
            )
            result = cursor.fetchall()
        return [row[0] for row in result]
