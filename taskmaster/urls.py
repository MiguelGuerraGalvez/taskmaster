from django.urls import path
from .views import HomeView, TaskCreateView, TasksDeleteView, LoginView, RegisterView, ProjectListView, ProjectCreateView, ProjectDeleteView, ProjectUpdateView, TaskUpdateStatus, TaskUpdateView, ProjectDetailView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/tasks/<int:pk>', ProjectDetailView.as_view(), name='task_list'),
    path('projects/tasks/<int:pk>/status/<str_status>', TaskUpdateStatus.as_view(), name='task_status'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/delete/<pk>', TasksDeleteView.as_view(), name='tasks_delete'),
    path('projects/tasks/update/<pk>', TaskUpdateView.as_view(), name='task_update'),
    path('projects/delete/<pk>', ProjectDeleteView.as_view(), name='project_delete'),
    path('projects/update/<pk>', ProjectUpdateView.as_view(), name='project_update'),
    path('projects/create/', ProjectCreateView.as_view(), name='project_create'),
]
