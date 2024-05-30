"""
Views for the task APIs.
"""
from django.forms import model_to_dict
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Task,
    TaskChangesHistory,
)
from task import serializers




class TaskViewSet(viewsets.ModelViewSet):
    """View for manage task APIs."""
    serializer_class = serializers.TaskSerializer
    queryset = Task.objects.all().order_by('-id')
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.TaskSerializer

        return serializers.TaskDetailSerializer
    
    def perform_create(self, serializer):
        """Create a new task."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update a task and create a change history record."""
        task = self.get_object()
        user = self.request.user

        task_snapshot = model_to_dict(
            task,
            fields=[
                'name',
                'description',
                'status',
                'assigned_to'
            ]
        )
        if task_snapshot['assigned_to']:
            task_snapshot['assigned_to'] = list(task.assigned_to.values_list('id', flat=True))

        super().perform_update(serializer)

        TaskChangesHistory.objects.create(
            task=task,
            changed_by=user,
            task_snapshot=task_snapshot,
            change_date=timezone.now(),
        )


