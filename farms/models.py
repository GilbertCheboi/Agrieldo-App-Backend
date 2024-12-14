# File: farms/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings  # Import settings to use the custom user model
    

class Farm(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')

    def __str__(self):
        return self.name
