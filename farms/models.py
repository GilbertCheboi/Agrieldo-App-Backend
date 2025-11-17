from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings
from pgvector.django import VectorField

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
        help_text="Latitude in decimal degrees"
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude in decimal degrees"
    )

    type = models.CharField(
        max_length=20,
        choices=FARM_TYPES,
        default='Dairy'
    )

    image = models.ImageField(upload_to="farms/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_sheet_url = models.URLField(blank=True, null=True)

    # ⭐ NEW: Azure OpenAI RAG field
    embedding = VectorField(dimensions=1536, null=True)

    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username}, Type: {self.type})"


    # ⭐ NEW: Auto-generate embedding
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Save first to get primary key
        super().save(*args, **kwargs)

        # Only generate embedding for new Farm objects
        if is_new:
            from rag.utils import generate_farm_embedding
            self.embedding = generate_farm_embedding(self)
            super().save(update_fields=["embedding"])


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

