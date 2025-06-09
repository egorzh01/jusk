from rest_framework import serializers

from apps.users.models import User

from .models import TaskTimeLog


class TimeLogSerializer(serializers.ModelSerializer[TaskTimeLog]):
    creator: serializers.StringRelatedField[User] = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = TaskTimeLog
        fields = ["id", "hours", "description", "creator", "created_at", "updated_at"]
