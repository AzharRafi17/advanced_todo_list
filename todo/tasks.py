
# from __future__import absolute_import, unicode_literals
# from celery import shared_task
# from celery.utils.log import get_task_logger
# from django.core.mail import send_mail,BadHeaderError
# from mytodo.settings import DEFAULT_FROM_EMAIL
# from django.conf import settings
# logger = get_task_logger(__name__)
# from django.utils.timezone import now
# from .models import Task

# @shared_task(bind=True)
# def send_task_reminder(self, to, subject,message,task_id):
#     task = Task.objects.get(id=task_id)
#     try:
#         send_mail(subject,message,settings.EMAIL_HOST_USER,[to])
#     except BadHeaderError:
#         logger.info("BadHeaderError")
#     except Exception as e:
#         logger.error(e)
#     send_mail(
#         f'Reminder: {task.title} is due soon!',
#         f'Dear {task.user.username}, your task "{task.title}" is due on {task.due_date}. Please complete it on time!',
#         'studypurpose220904@gmail.com',  # Replace with your sender email
#         [task.user.email],
#         fail_silently=False,
#     )


from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import Task

@shared_task(bind=True)
def send_task_reminder(self):
    #  tomorrow = now() + timedelta(days=1)
    #  tasks_due_tomorrow = Task.objects.filter(due_date__date=tomorrow.date())
    current_time = now()
    # Calculate the cutoff for tasks due more than one day from now
    due_date_cutoff = current_time + timedelta(days=1)

    # Get all tasks with a due date greater than the cutoff
    tasks_due_later = Task.objects.filter(due_date__gt=due_date_cutoff)


    for task in tasks_due_later:
        send_mail(
            f'Reminder: {task.title} is due tomorrow!',
            f'Dear {task.user.username}, your task "{task.title}" is due on {task.due_date}. Please complete it on time!',
            'muhammadazharali17@gmail.com',  # Replace with your sender email
            [task.user.email],
            fail_silently=False,
        )
    