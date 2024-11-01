from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import Task
@shared_task(bind=True)
def send_task_reminder(self):
    #  tomorrow = now() + timedelta(days=1)
    #  tasks_due_tomorrow = Task.objects.filter(due_date__date=tomorrow.date())
    current_time = now()
    due_date_cutoff = current_time + timedelta(days=1)
    tasks_due_later = Task.objects.filter(due_date__gt=due_date_cutoff)


    for task in tasks_due_later:
        send_mail(
            f'Reminder: {task.title} is due tomorrow!',
            f'Dear {task.user.username}, your task "{task.title}" is due on {task.due_date}. Please complete it on time!',
            'muhammadazharali17@gmail.com',  
            [task.user.email],
            fail_silently=False,
        )
        send_task_reminder.delay()