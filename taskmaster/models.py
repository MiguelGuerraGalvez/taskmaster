from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    collaborators = models.ManyToManyField(User, related_name="collaborated_projects", blank=True)

    def __str__(self):
        return self.title
    
    def total_tasks(self):
        return self.tasks.count()
    
    def total_tasks_done(self):
        return self.tasks.filter(status='DONE').count()


class Task(models.Model):
    STATUS_CHOICES = [
        ("TODO", "Pendiente"),
        ("IN_PROGRESS", "En Progreso"),
        ("DONE", "Completada")
    ]

    PRIORITY_CHOICES = [
        ("L", "Baja"),
        ("M", "Media"),
        ("H", "Alta")
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=False, blank=False)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="TODO")
    priority = models.CharField(max_length=255, choices=PRIORITY_CHOICES, default="M")
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.project.title})"
    
    def save(self, *args, **kwargs):
        print("TASK SAVE", self.pk)
        super().save(*args, **kwargs)

