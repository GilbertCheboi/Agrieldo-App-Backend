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


class Staff(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile'
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True )
    farm_location = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='staff_images/', null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)  # New field for first name
    second_name = models.CharField(max_length=100, null=True, blank=True )  # New field for second name
    banner = models.ImageField(upload_to='staff_banner_images/', null=True, blank=True)


    def __str__(self):
        return f"Staff Profile for {self.user.username}"


class Lead(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=15, blank=True, null=True)

    source = models.CharField(
        max_length=100,
        choices=[('Campaign', 'Campaign'), ('Referral', 'Referral'), ('Other', 'Other')],
        default='Campaign'
    )
    referral_name = models.CharField(max_length=100, blank=True, null=True)  # New field for referral name
    referral_phone_number = models.CharField(max_length=15, blank=True, null=True)  # New field for referral phone number
    status = models.CharField(
        max_length=50,
        choices=[
            ('New', 'New'),
            ('Contacted', 'Contacted'),
            ('Converted', 'Converted'),
            ('Follow-up', 'Follow-up'),
            ('Interested', 'Interested'),
            ('Lost', 'Lost')
        ],
        default='New'
    )
    description = models.TextField(blank=True, null=True)  # Description field to store user input
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"

