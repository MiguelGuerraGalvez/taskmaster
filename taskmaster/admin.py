from django.contrib import admin
from .models import Project, Task

# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'deadline', 'owner')
    list_editable = ('description', 'deadline')
    list_filter = ('title', 'description', 'deadline', 'owner', 'collaborators')
    search_fields = ()
    readonly_fields = ('created_at',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'description', 'status', 'priority')
    list_editable = ('title', 'description', 'status', 'priority')
    list_filter = ('title', 'description', 'status', 'priority')
    search_fields = ()
    readonly_fields = ()
