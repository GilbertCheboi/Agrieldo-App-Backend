from django.db import models
from django.conf import settings

class Farm(models.Model):
    FARM_TYPES = (
        ('Dairy', 'Dairy'),
        ('Sheep', 'Sheep'),
        ('Crop', 'Crop'),
    )
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_farms'
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude in decimal degrees (e.g., 40.7128)"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude in decimal degrees (e.g., -74.0060)"
    )
    type = models.CharField(
        max_length=20,
        choices=FARM_TYPES,
        default='Dairy',  # Default to Dairy, adjust as needed
        help_text="Type of farm (Dairy, Sheep, Crop)"
    )

    image = models.ImageField(
        upload_to="farms/",
        blank=True,
        null=True,
        help_text="Image of the farm"
    )

     # ✅ timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # set once when created
    updated_at = models.DateTimeField(auto_now=True)      # updates on each save
    google_sheet_url = models.URLField(blank=True, null=True)  # 👈 Link to Google Sheet


    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username}, Type: {self.type})"


class FarmStaff(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="farm_staff")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_farms"
    )

    class Meta:
        unique_together = ("farm", "user")  # Prevent duplicate assignments

    def __str__(self):
        return f"{self.user.username} - {self.farm.name}"


class FarmVet(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="vet_staff")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_vet_farms"
    )

    class Meta:
        unique_together = ("farm", "user")  # Prevent duplicate assignments

    def __str__(self):
        return f"{self.user.username} - {self.farm.name}"

