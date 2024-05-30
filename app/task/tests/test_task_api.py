"""
Tests for task API.
"""
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Task,
    TaskChangesHistory,
)
from task.serializers import (
    TaskSerializer,
    TaskDetailSerializer,
    TaskChangesHistorySerializer
)


TASK_URL = reverse('task:task-list')


def detail_url(task_id):
    """Create and return a task detail URL."""
    return reverse('task:task-detail', args=[task_id])


def create_task(user, **kwargs):
    """Create and return a sample task."""
    defaults = {
        'name': 'Test task',
        'description': 'Test description',
        'status': 'new',
    }
    defaults.update(kwargs)

    task = Task.objects.create(user=user, **defaults)
    return task


def create_user(**kwargs):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**kwargs)


class PublicTaskApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(TASK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTaskApiTests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='Test@example.com',
            password='Test123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tasks(self):
        """Test retrieving a list of tasks."""
        create_task(name='task1', user=self.user)
        create_task(name='task2', user=self.user)

        res = self.client.get(TASK_URL)

        tasks = Task.objects.all().order_by('-id')
        serializer = TaskSerializer(tasks, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_task_detail(self):
        """Test get task detail."""
        task = create_task(user=self.user)

        url = detail_url(task.id)
        res = self.client.get(url)

        serializer = TaskDetailSerializer(task)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_task_successful(self):
        """Test creating a task successful."""
        payload = {
            'name': 'Test nam',
            'description': 'Test description',
            'status': 'new',
        }
        res = self.client.post(TASK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.user, self.user)

    def test_create_task_with_assigned_users(self):
        """Test creating a task with assigned users successful."""
        user1 = create_user(email='test2@example.com', password='Test123')
        user2 = create_user(email='test3@example.com', password='Test123')
        payload = {
            'name': 'test name',
            'description': 'test description',
            'status': 'in_progress',
            'assigned_to': [user1.id, user2.id]
        }
        res = self.client.post(TASK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=res.data['id'])
        assigned_users = task.assigned_to.all()
        for user_id in payload['assigned_to']:
            self.assertIn(user_id, [user.id for user in assigned_users])
        self.assertEqual(assigned_users.count(), len(payload['assigned_to']))

    def test_add_assigned_user_to_exist_task(self):
        """Test that a user can be assigned to an existing task."""
        user1 = create_user(email='test2@example.com', password='Test123')
        user2 = create_user(email='test3@example.com', password='Test123')
        task = create_task(user=self.user)

        payload = {'assigned_to': [user1.id, user2.id]}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)
        assigned_users = task.assigned_to.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for user_id in payload['assigned_to']:
            self.assertIn(user_id, [user.id for user in assigned_users])
        self.assertEqual(assigned_users.count(), len(payload['assigned_to']))

    def test_create_task_wrong_status(self):
        """Test that an error is returned if an invalid status is provided."""
        payload = {
            'name': 'Test nam',
            'description': 'Test description',
            'status': 'wrong',
        }
        res = self.client.post(TASK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        task = Task.objects.filter(name=payload['name']).exists()
        self.assertFalse(task)

    def test_partial_update(self):
        """Test partial update of a task."""
        task = create_task(user=self.user)

        payload = {'name': 'updated task name'}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.name, payload['name'])
        self.assertEqual(task.user, self.user)

    def test_full_update(self):
        """Test full update of a task."""
        task = create_task(user=self.user)
        payload = {
            'name': 'updated task name',
            'description': 'updated description name',
            'status': 'in_progress',
        }
        url = detail_url(task.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(task, k), v)
        self.assertEqual(task.user, self.user)

    def test_update_user_returns_error(self):
        new_user = create_user(email='example2@test.com', password="Test123")
        task = create_task(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.user, self.user)

    def test_delete_task(self):
        """Test deleting a task successful."""
        task = create_task(user=self.user)

        url = detail_url(task.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_task_changes_history_created_on_update(self):
        """Test that a task changes history record is created on task update."""
        task = create_task(user=self.user)
        payload = {'name': 'updated test name'}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        changes = TaskChangesHistory.objects.filter(task=task)
        self.assertEqual(changes.count(), 1)

    def test_task_changes_history_snapshot_data(self):
        """Test that the task changes history record contains the correct snapshot data."""
        task = create_task(user=self.user)
        task_snapshot = model_to_dict(
            task,
            fields=['name', 'description', 'status', 'assigned_to']
        )
        if task_snapshot['assigned_to']:
            task_snapshot['assigned_to'] = task.assigned_to.id

        payload = {'name': 'Changed name'}
        url = detail_url(task.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        changes = TaskChangesHistory.objects.filter(task=task)
        change_history = changes.first()
        for field in task_snapshot.keys():
            self.assertEqual(change_history.task_snapshot[field], task_snapshot[field])

    def test_retrieve_task_with_last_10_changes(self):
        """Test retrieving a task with its last 10 changes."""
        task = create_task(user=self.user)
        for i in range(15):
            TaskChangesHistory.objects.create(
                task=task,
                changed_by=self.user,
                change_date=timezone.now() - timezone.timedelta(days=i),
                task_snapshot={
                    'name': f'Old Task Name {i}',
                    'description': f'Old Task Description {i}',
                    'status': 'new',
                    'assigned_to': None,
                }
            )

        url = detail_url(task.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['changes']), 10)
        changes = TaskChangesHistory.objects.filter(task=task).order_by('-change_date')[:10]
        serializer = TaskChangesHistorySerializer(changes, many=True)
        self.assertEqual(res.data['changes'], serializer.data)
