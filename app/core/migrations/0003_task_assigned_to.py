# Generated by Django 5.0.6 on 2024-05-30 15:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_task"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="assigned_to",
            field=models.ManyToManyField(
                blank=True, related_name="tasks_assigned", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
