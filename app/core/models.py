"""
Databases models.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **kwargs):
        """Create and return a new user."""
        if not email:
            raise ValueError('Email is required.')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Task(models.Model):
    """Model for task object."""
    STATUS_CHOICES = [
        ('new', 'NEW'),
        ('in_progress', 'In progress'),
        ('done', 'Done')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    assigned_to = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tasks_assigned',
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        default='new',
        choices=STATUS_CHOICES,
    )

    def __str__(self):
        return self.name


class TaskChangesHistory(models.Model):
    """Model to track changes in tasks."""
    task = models.ForeignKey('Task',
                             on_delete=models.CASCADE,
                             related_name='changes',)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE)
    change_date = models.DateTimeField(default=timezone.now)
    task_snapshot = models.JSONField()

    def __str__(self):
        return f"Change in task {self.task.id} by {self.changed_by.email} on {self.change_date}"
