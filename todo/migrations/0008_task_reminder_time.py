# Generated by Django 5.1.1 on 2024-10-23 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0007_alter_task_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='reminder_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
