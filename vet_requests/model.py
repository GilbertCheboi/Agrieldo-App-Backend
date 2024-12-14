from django.db import models

class VetRequest(models.Model):
    farmer_name = models.CharField(max_length=100)
    issue_description = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    
    # New field for farm location
    farm_location = models.CharField(max_length=255)  # Name of the location or address

    # Optional: If you want to store coordinates, you can add these fields as well
    latitude = models.FloatField(null=True, blank=True)  # For storing latitude
    longitude = models.FloatField(null=True, blank=True)  # For storing longitude

    def __str__(self):
        return f"{self.farmer_name} - {self.status} at {self.farm_location}"

