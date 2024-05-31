"""
Tests for models.
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict

from core import models


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successufl."""
        email = "test@example.com"
        password = "Pass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password="Test123",
            )
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raiser_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email="",
                password="Test123",
            )

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email="example@test.com",
            password="Test123",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_task(self):
        """Test creating a task is successful."""
        user = get_user_model().objects.create_user(
            email="example@test.com",
            password="Pass123",
        )
        task = models.Task.objects.create(
            user=user,
            name="Test Name",
            description="Test Desc",
            status="in_progress",
        )

        self.assertEqual(str(task), task.name)

    def test_create_task_change_history(self):
        """Test that creating a task change history record is successful."""
        user1 = get_user_model().objects.create_user(
            email="example@test.com",
            password="Pass123",
        )
        user2 = get_user_model().objects.create_user(
            email="test@test.com",
            password="Pass123",
        )
        task = models.Task.objects.create(
            user=user1,
            name="Test Name",
            description="Test Desc",
            status="in_progress",
        )
        change_date = timezone.now()
        task_snapshot = model_to_dict(
            task,
            fields=[
                "name",
                "description",
                "status",
                "assigned_to",
            ],
        )

        change_history = models.TaskChangesHistory.objects.create(
            task=task,
            changed_by=user2,
            change_date=change_date,
            task_snapshot=task_snapshot,
        )
        expected_str = f"Change in task {task.id} by {user2.email} on {change_date}"
        self.assertEqual(str(change_history), expected_str)
