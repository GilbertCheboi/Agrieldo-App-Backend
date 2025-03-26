from django.db import models
from django.conf import settings
from django.utils.timezone import now

from django.db import models
from django.utils.timezone import now
import os

class Feed(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    quantity_kg = models.FloatField(default=0.0, null=True, blank=True)
    price_per_kg = models.FloatField(default=0.0, help_text="Cost per kg")  # Added
    created_at = models.DateTimeField(default=now, null=True, blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeds_farm',
        null=True,
        blank=True
    )

    def deduct_feed(self, quantity):
        if self.quantity_kg >= quantity:
            self.quantity_kg -= quantity
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.name} - {self.quantity_kg} kg"
