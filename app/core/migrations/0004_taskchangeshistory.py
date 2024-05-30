# Generated by Django 5.0.6 on 2024-05-30 17:52

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_task_assigned_to'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskChangesHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('task_snapshot', models.JSONField()),
                ('changed_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='core.task')),
            ],
        ),
    ]