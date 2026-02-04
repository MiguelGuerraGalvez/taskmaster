from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, DeleteView, UpdateView, DetailView
from .models import Project, Task
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

# Create your views here.
def error404(request, exception):
    return render(request, '404.html')

class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        return render(request, self.template_name)

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "project_list.html"
    context_object_name = "projects"
    login_url = '/login/'

    def get_queryset(self):
        return Project.objects.filter(Q(owner=self.request.user) | Q(collaborators=self.request.user)).order_by("deadline")

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'deadline', 'collaborators']
        widgets = {'deadline': forms.DateInput(attrs={'type': 'date'})}
    
    def __init__(self, *args, **kwargs):
        # Cogemos al usuario
        self.user = kwargs.pop('user', None)
        super(ProjectForm, self).__init__(*args, **kwargs)

        # Si tenemos al usuario, lo quitamos de los colaboradores
        if self.user:
            self.fields['collaborators'].queryset = User.objects.exclude(id=self.user.id)
    
    def clean_collaborators(self):
        collaborators = self.cleaned_data.get('collaborators')
        if self.user in collaborators:
            raise forms.ValidationError("No puedes ser colaborador y creador a la vez")
        else:
            return collaborators

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline < timezone.now().date():
            raise forms.ValidationError("No puede ser una fecha pasada")
        else:
            return deadline

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = "project_create.html"
    form_class = ProjectForm
    success_url = '/projects/'
    login_url = '/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = "confirm_delete.html"
    success_url = '/projects/'
    login_url = '/login/'

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = "project_update.html"
    form_class = ProjectForm
    success_url = "/projects/"
    login_url = '/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "task_list.html"
    context_object_name = "project"
    login_url = '/login/'

    # def get_queryset(self):
    #     return Task.objects.filter(project_id=self.kwargs['project_id']).order_by("project__deadline")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        context['tasks'] = project.tasks.order_by("project__deadline")
        context['total_tasks'] = project.tasks.count()
        context['done_tasks'] = project.tasks.filter(status='DONE').count() * 100 / project.tasks.count()
        context['labels'] = ["Completadas", "No completadas"]
        # context['project_id'] = self.kwargs['project_id']
        return context

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'status', 'priority', 'assigned_to']
    
    def __init__(self, *args, **kwargs):
        # Cogemos el proyecto
        self.user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)

        self.fields['description'].required = False

        # Quitamos los que no son ni propietarios ni colaboradores
        if self.user:
            self.fields['project'].queryset = Project.objects.filter(Q(owner=self.user) | Q(collaborators=self.user)).distinct()
            self.fields['assigned_to'].queryset = User.objects.filter(Q(owned_projects__in=self.fields['project'].queryset) | Q(collaborated_projects__in=self.fields['project'].queryset)).distinct()
        
    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        assigned_to = cleaned_data.get('assigned_to')

        if project and assigned_to:
            # Verificamos que el usuario asignado sea el creador o un colaborador
            is_owner = (project.owner == assigned_to)
            is_collaborator = project.collaborators.filter(id=assigned_to.id).exists()

            if not is_owner and not is_collaborator:
                raise forms.ValidationError("No puedes asignarle la tarea a alguien que no sea el creador o colaborador")

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "task_create.html"
    form_class = TaskForm
    login_url = '/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return f'/projects/tasks/{self.object.project.id}'

    def form_valid(self, form):
        return super().form_valid(form)
    
class TasksDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "confirm_delete.html"
    login_url = '/login/'

    def get_success_url(self):
        return f'/projects/tasks/{self.object.project.id}'

class TaskUpdateStatus(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk, str_status):
        task = get_object_or_404(Task, pk=pk)
        task.status = str_status
        task.save()
    
        return redirect(request.META.get('HTTP_REFERER', '/projects/'))

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = "task_update.html"
    form_class = TaskForm
    login_url = '/login/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return f'/projects/tasks/{self.object.project.id}'

class AnonymousMixin(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('/tasks/')

class LoginView(AnonymousMixin, auth_views.LoginView):
    template_name = 'registration/login.html'

class RegisterView(AnonymousMixin, CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = '/login/'
