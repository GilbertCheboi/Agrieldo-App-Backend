from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    FARMER = 1
    VET = 2

    USER_TYPE_CHOICES = (
        (FARMER, 'Farmer'),
        (VET, 'Vet'),
    )

    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=FARMER)  # Default to Farmer

    # Add additional fields
    email = models.EmailField(unique=True, null=False, blank=False)  # Make email required and unique
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Remove `unique=True` temporarily

    fcm_token = models.CharField(max_length=255, blank=True, null=True, help_text="Firebase Cloud Messaging token")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

# Password reset token model
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(hours=1))  # Token expires after 1 hour

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Token for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timedelta(hours=1)  # Automatically set expiration date on creation
        super().save(*args, **kwargs)
