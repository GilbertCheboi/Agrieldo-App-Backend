from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "farm", "assigned_to", "status", "due_date")
    list_filter = ("status", "farm", "assigned_to")
    search_fields = ("title", "description", "assigned_to__username", "farm__name")

