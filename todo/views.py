from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Task, Category
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from .tasks import send_task_reminder
from django.utils import timezone


@login_required(login_url='login')
def todoList(request):
    # returns the tasks of the current user
    todos = Task.objects.filter(user=request.user)
    
    selected_category = request.GET.get('category')
    # title_search = request.GET.get('title')
    
    # if title_search:
    #     todos = todos.filter(title__icontains=title_search)
    
    if selected_category:
        todos = todos.filter(category__name=selected_category)
    
    sort_by = request.GET.get('sort_by')
    # search = request.GET.get('search')
    # print(f'search {search}')
    # if search:
    #     todos = todos.filter(title__startswith=search)
    #     print(f'todos {todos}')
    
    # CSV file input code
    # if request.method == 'POST':
    #     file = request.FILES['file']        
    
    #     decoded_file = io.TextIOWrapper(file.file, encoding="utf-8")
    #     reader = csv.reader(decoded_file, delimiter=",")
    #     # print(reader)
        
    #     for row in reader:
    #         title = row[0]        
    #         description = row[1]
    #         due_date = row[2]
    #         priority = row[3]
    #         category = row[4]
    #         category = Category.objects.create(name=category)
    #         due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
    #         Task.objects.create(user=request.user, title=title, desciption = description, priority=priority, due_date=due_date, category=category)
        
    #     return redirect('todo_list')

    # search_query = request.GET.get('search', '')
    # if search_query:
    #     # Filter tasks based on the search query
    #     todos = todos.filter(title__startswith=search_query)
        
    # if request.headers.get('HX-Request') == 'true':
    #     # Return only the partial template
    #     return render(request, 'todo_list.html', {'todos': todos})
    
    if sort_by == 'due_date_desc':
        todos = todos.order_by('-due_date')
    elif sort_by == 'due_date_asc':
        todos = todos.order_by('due_date')
    elif sort_by == 'priority_asc':
        todos = todos.order_by('priority')
    elif sort_by == 'priority_desc':
        todos = todos.order_by('-priority')
    
    # For sending emails to the user
    # for task in todos:
    #     reminder_time = task.due_date - timedelta(days=1)   # Calculate the reminder time: 1 day before the due date
    #     # now = timezone.now()
    #     # if reminder_time > now:
    #     send_task_reminder.apply_async((task.id,), eta=reminder_time) # eta = estimated time of arrival

    return render(request, 'index.html', {'todos': todos})
    
@login_required(login_url='login')
def create_todo(request):
    if request.method == 'POST':
        desciption = request.POST.get('description')
        title = request.POST.get('title')
        priority = request.POST.get('priority') or 1
        duedate = request.POST.get('duedate')
        category = request.POST.get('category')
        category = Category.objects.create(name=category)
        reminder_time = request.POST.get('reminder_time')
        
        task = Task( 
            title=title,
            desciption=desciption,
            due_date=duedate,
            reminder_time=reminder_time,
            category=category,
            priority=priority,
            user=request.user
        )
        task.save()
        return redirect('todo_list')
    return render(request, 'index.html', {'reminder': reminder_time})

@login_required(login_url='login')
def complete_todo(request, todo_id):
    todo = Task.objects.get(id=todo_id, user=request.user)
    todo.completed = True
    todo.save()
    return redirect('todo_list')

@login_required(login_url='login')
def delete_todo(request, todo_id):
    todo = Task.objects.get(id=todo_id, user=request.user)
    todo.delete()
    return redirect('todo_list')

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request,"Invalid username or password")
            return redirect('login')
        
        user = authenticate(username = username, password= password) 

        if user is None:   
            messages.error(request,"Invalid Credentials")
            return redirect('login')
        
        else:   
            login(request, user)
            return redirect('todo_list')
    
    
    return render(request,'login.html')
    
    
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username = username)
        
        if user.exists():
            messages.info(request, "User already taken")
            return redirect('register')
        
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.save()
        
        messages.info(request,"Account created successfully")
        
        return redirect('register')
    return render (request,'register.html')

def logout_page(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'home.html')



@login_required(login_url='login')
def edit_task(request, todo_id):
    
    task = Task.objects.get(id=todo_id)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.desciption = request.POST.get('description')
        task.priority = request.POST.get('priority') or 1
        task.due_date = request.POST.get('due_date')
        task.reminder_time = request.POST.get('reminder_time')
        category_name = request.POST.get('category')
        categories = Category.objects.filter(name=category_name)
        
        if categories.exists():
            category = categories.first()  # Get the first category found
        else:
        # Optionally create the category if it doesn't exist
            category = Category.objects.create(name=category_name)

        task.category = category
        task.save()
        return redirect('todo_list')
    
    return render(request, 'edit.html', {'task':task})


@login_required(login_url='login')
def create_task(request):
    if request.method == 'POST':
        desciption = request.POST.get('description')
        title = request.POST.get('title')
        priority = request.POST.get('priority') or 1
        due_date = request.POST.get('duedate')
        category_name = request.POST.get('category')
        reminder_time_str = request.POST.get('reminder_time')

        # Create or get the category
        category, created = Category.objects.get_or_create(name=category_name)

        # Convert reminder_time_str to a datetime object if provided
        reminder_time = None
        if reminder_time_str:
            reminder_time = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')  # Adjust format as needed

        # Create a new task
        task = Task(
            title=title,
            desciption=desciption,
            due_date=due_date,
            reminder_time=reminder_time,
            category=category,
            priority=priority,
            user=request.user
        )
        task.save()

        return redirect('todo_list')

    return render(request, 'index.html')  


# @login_required(login_url='login')
# def get_title(request):
    
#     search = request.GET.get('search','')
#     payload = []

#     if search:
#         objs = Task.objects.filter(user=request.user,title__startswith=search)
#         for obj in objs:
#             print(f"obj {obj}")
#             payload.append({
#                 "title": obj.title
#             })
        
#     return JsonResponse({
#         "status": True,
#         "payload": payload
#     })
 






























































# from django.http import JsonResponse
# from django.shortcuts import render, redirect,get_object_or_404
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from .models import Task, Category
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from .tasks import send_task_reminder
# import json
# from datetime import datetime, timedelta    
# from django.conf import settings
# from celery import shared_task


# @login_required(login_url='login')
# def todoList(request):
#     # returns the tasks of the current user
#     todos = Task.objects.filter(user=request.user)
    
#     selected_category = request.GET.get('category')
    
#     if selected_category:
#         todos = todos.filter(category__name=selected_category)
    
#     sort_by = request.GET.get('sort_by')
    
#     if sort_by == 'due_date_desc':
#         todos = todos.order_by('-due_date')
#     elif sort_by == 'due_date_asc':
#         todos = todos.order_by('due_date')
#     elif sort_by == 'priority_asc':
#         todos = todos.order_by('priority')
#     elif sort_by == 'priority_desc':
#         todos = todos.order_by('-priority')
#     current_time = timezone.now()
#     reminder_tasks = todos.filter(
#         reminder_time__gte=current_time,
#         reminder_time__lte=current_time + timezone.timedelta(hours=1)
#     )

#     # Check for reminder tasks to send emails (if needed)
#     if reminder_tasks.exists():  
#         for task in reminder_tasks:
#             send_task_reminder(
#                 subject=f'Reminder: {task.title}',
#                 message=f'You have a task due soon: {task.title}. Reminder Time: {task.reminder_time.strftime("%Y-%m-%d %H:%M")}.',
#                 from_email='muhammadazharali17@gmail.com',  # Change to your email
#                 recipient_list=[request.user.email],
#                 fail_silently=False,
#             )
#         if reminder_tasks.exists():
#          for task in reminder_tasks:
#             send_task_reminder.delay()
#             # return redirect('todo_list')

#     # return redirect('todo_list')

#     # Render your template with all tasks
   
# @login_required(login_url='login')
# def create_todo(request):
#     if request.method == 'POST':
#         desciption = request.POST.get('description')
#         title = request.POST.get('title')
#         priority = request.POST.get('priority') or 1
#         duedate = request.POST.get('duedate')
#         category = request.POST.get('category')
#         category = Category.objects.create(name=category)
#         reminder_time = request.POST.get('reminder_time')
        
#         task = Task( 
#             title=title,
#             desciption=desciption,
#             due_date=duedate,
#             reminder_time=reminder_time,
#             category=category,
#             priority=priority,
#             user=request.user
#         )
#         task.save()
#         return redirect('todo_list')
#     return render(request, 'index.html', {'reminder': reminder_time})
    
# @login_required(login_url='login')
# def pending_task(request,):
#     tasks = Task.objects.filter(user=request.user,completed=False)
#     pending_tasks = []

#     for task in tasks:
#         if task.reminder_time and task.reminder_time > timezone.now():
#             # Calculate the time remaining until the reminder
#             time_remaining = (task.reminder_time - timezone.now()).total_seconds()
#             pending_tasks.append((task, time_remaining))

#     return render(request, 'task.html', {'tasks': tasks, 'pending_tasks': pending_tasks})
# @login_required(login_url='login')
# def complete_todo(request, todo_id):
#     todo = Task.objects.get(id=todo_id, user=request.user)
#     todo.completed = True
#     todo.save()
#     return redirect('todo_list')

# @login_required(login_url='login')
# def delete_todo(request, todo_id):
#     todo = Task.objects.get(id=todo_id, user=request.user)
#     todo.delete()
#     return redirect('todo_list')

# def login_page(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         if not User.objects.filter(username=username).exists():
#             messages.error(request,"Invalid username or password")
#             return redirect('login')
        
#         user = authenticate(username = username, password= password) 

#         if user is None:   
#             messages.error(request,"Invalid Credentials")
#             return redirect('login')
        
#         else:   
#             login(request, user)
#             return redirect('todo_list')
    
    
#     return render(request,'login.html')
    
# def register(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')
        
#         user = User.objects.filter(username = username)
        
#         if user.exists():
#             messages.info(request, "User already taken")
#             return redirect('register')
        
#         user = User.objects.create_user(username=username)
#         user.set_password(password)
#         user.save()
        
#         messages.info(request,"Account created successfully")
        
#         return redirect('register')
#     return render (request,'register.html')

# def logout_page(request):
#     logout(request)
#     return redirect('login')

# def home(request):
#     return render(request, 'home.html')


# @login_required(login_url='login')
# def edit_task(request, todo_id):
    
#     task = Task.objects.get(id=todo_id)
    
#     if request.method == 'POST':
#         task.title = request.POST.get('title')
#         task.desciption = request.POST.get('description')
#         task.priority = request.POST.get('priority') or 1
#         task.due_date = request.POST.get('due_date')
#         task.reminder_time = request.POST.get('reminder_time')
#         category_name = request.POST.get('category')
#         categories = Category.objects.filter(name=category_name)
        
#         if categories.exists():
#             category = categories.first()  # Get the first category found
#         else:
#         # Optionally create the category if it doesn't exist
#             category = Category.objects.create(name=category_name)

#         task.category = category
#         task.save()
#         return redirect('todo_list')
    
#     return render(request, 'edit.html', {'task':task})

# @login_required(login_url='login')
# def create_task(request):
#     if request.method == 'POST':
#         desciption = request.POST.get('description')
#         title = request.POST.get('title')
#         priority = request.POST.get('priority') or 1
#         due_date = request.POST.get('duedate')
#         category_name = request.POST.get('category')
#         reminder_time_str = request.POST.get('reminder_time')

#         # Create or get the category
#         category, created = Category.objects.get_or_create(name=category_name)

#         # Convert reminder_time_str to a datetime object if provided
#         reminder_time = None
#         if reminder_time_str:
#             reminder_time = datetime.strptime(reminder_time_str, '%Y-%m-%d %H:%M')  # Adjust format as needed

#         # Create a new task
#         task = Task(
#             title=title,
#             desciption=desciption,
#             due_date=due_date,
#             reminder_time=reminder_time,
#             category=category,
#             priority=priority,
#             user=request.user
#         )
#         send_task_reminder(request.user.email, task.title, reminder_time)
#         task.save()

#         # Schedule the email reminder using Celery if reminder_time is set
#         if reminder_time.exists():
#          for task in reminder_time:
#             send_task_reminder.delay()
#         if reminder_time:
#             reminder_delay = (reminder_time - timezone.now()).total_seconds()
#             send_reminder_email_task.apply_async((request.user.email, title), countdown=reminder_delay)

#         return redirect('todo_list')

#     return render(request, 'index.html')  

# @shared_task
# def send_reminder_email_task(to_email, task_name): 
#     subject = 'Task Reminder'
#     message = f'Reminder: You have a pending task - "{task_name}".'
#     from_email = settings.DEFAULT_FROM_EMAIL

#     send_reminder_email_task(subject, message, from_email, [to_email])
#     print(to_email,subject,message)
#     send_reminder_email_task.delay()



