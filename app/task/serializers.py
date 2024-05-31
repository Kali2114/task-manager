"""
Serializers for task APIs.
"""

from rest_framework import serializers

from core.models import (
    Task,
    TaskChangesHistory,
)


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for tasks."""

    class Meta:
        model = Task
        fields = ["id", "name", "assigned_to", "status"]
        read_only_fields = ["id"]

    def validate_status(self, value):
        """Check that the status is one of the allowed values."""
        if value not in dict(Task.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Invalid status.")
        return value


class TaskDetailSerializer(TaskSerializer):
    """Serializer for task detail view."""

    changes = serializers.SerializerMethodField()

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ["description", "user", "changes"]
        read_only_fields = ["user", "changes"]

    def get_changes(self, obj):
        """Retrieve the last 10 changes for the given task."""
        changes = obj.changes.order_by("-change_date")
        return TaskChangesHistorySerializer(changes, many=True).data


class TaskChangesHistorySerializer(serializers.ModelSerializer):
    """Serializer for task changes history."""

    class Meta:
        model = TaskChangesHistory
        fields = ["id", "task", "changed_by", "change_date", "task_snapshot"]
        read_only_fields = fields
