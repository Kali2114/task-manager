"""
Filters for task API.
"""
from django_filters import rest_framework as filters

from core.models import Task


class TaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='iconstains')
    status = filters.ChoiceFilter(field_name='status', choices=Task.STATUS_CHOICES)
    assigned_to = filters.NumberFilter(field_name='assigned_to__id')

    class Meta:
        model = Task
        fields = ['id', 'name', 'description', 'status', 'user', 'assigned_to']
