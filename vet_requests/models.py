from django.db import models
from django.utils import timezone
from profiles.models import Vet, Farmer



class VetRequest(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, default='Jerry')
    vet = models.ForeignKey(Vet, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('unassigned', 'Unassigned')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    last_assigned_at = models.DateTimeField(default=timezone.now)

    def assign_to_vet(self, vet):
        self.vet = vet
        self.last_assigned_at = timezone.now()
        self.status = 'pending'
        self.save()
