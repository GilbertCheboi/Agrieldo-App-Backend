from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source="assigned_to.username", read_only=True)
    assigned_to_email = serializers.EmailField(source="assigned_to.email", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "due_date",  "status", "assigned_to", "assigned_to_username", "assigned_to_email"]
