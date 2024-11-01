from django.urls import path
from . import views
# . means that we are importing from the same folder

urlpatterns = [
    path('', views.home,name="home"),
    path('edit/<int:todo_id>', views.edit_task,name="edit_task"),
    path('register/', views.register,name="register"),
    path('todo/', views.todoList,name="todo_list"),
    path('logout/', views.logout_page,name="logout"),
    path('login/',views.login_page,name='login'),
    path('create/', views.create_todo,name="create_todo"),
    path('complete/<int:todo_id>', views.complete_todo,name="complete_todo"),
    path('delete/<int:todo_id>', views.delete_todo,name="delete_todo"),
    path('tasks/', views.create_task, name="create_task"),
    # path('task/',views.pending_task,name='pending_task' ),
]
#   path('', views.home,name="home"),
#     path('edit/<int:todo_id>', views.edit_task,name="edit_task"),
#     path('register/', views.register,name="register"),
#     path('todo/', views.todoList,name="todo_list"),
#     path('logout', views.logout_page,name="logout"),
#     path('login/',views.login_page,name='login'),
#     path('create', views.create_todo,name="create_todo"),
#     path('complete/<int:todo_id>', views.complete_todo,name="complete_todo"),
#     path('delete/<int:todo_id>', views.delete_todo,name="delete_todo"),