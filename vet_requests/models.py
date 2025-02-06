from django.db import models
from django.utils import timezone
from profiles.models import Vet, Farmer
from django.conf import settings




class VetRequest(models.Model):

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vet_requests'
    )


    
  # This could also be a Lat/Lng or Point field (Geospatial)
    description = models.TextField(null=True, blank=True)
    service_type = models.CharField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('unassigned', 'Unassigned')], default='pending')
    vet = models.ForeignKey(Vet, on_delete=models.SET_NULL, null=True, blank=True)

    image = models.ImageField(upload_to='vet_requests/', null=True, blank=True)  # To store image
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Request for {self.service_type} at {self.location} - {self.created_at}"

    def assign_to_vet(self, vet):
        self.vet = vet
        self.last_assigned_at = timezone.now()
        self.status = 'pending'
        self.save()

