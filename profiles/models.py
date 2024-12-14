from django.conf import settings
from django.db import models

class Vet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vet_profile'
    )
    phone_number = models.CharField(max_length=15)
    is_available = models.BooleanField(default=True)
    last_active = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Vet Profile for {self.user.username}"

class Farmer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='farmer_profile'
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True )
    farm_location = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='farmer_images/', null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)  # New field for first name
    second_name = models.CharField(max_length=100, null=True, blank=True )  # New field for second name
    banner = models.ImageField(upload_to='banner_images/', null=True, blank=True)


    def __str__(self):
        return f"Farmer Profile for {self.user.username}"


