from django.db import models
from django.conf import settings
from django.utils.timezone import now

from django.db import models
from django.utils.timezone import now
import os

class Feed(models.Model):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    quantity_kg = models.FloatField(default=0.0, null=True, blank=True)
    created_at = models.DateTimeField(default=now, null=True, blank=True)
    image = models.ImageField(upload_to='feed_images/', null=True, blank=True)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeds_farm',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.quantity_kg} kg"




class FeedTransaction(models.Model):
    FEED_ACTIONS = [
        ('ADD', 'Added'),
        ('CONSUME', 'Consumed')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeds',
        null=True,
        blank=True
    )

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, null=True, blank=True)
    quantity_kg = models.FloatField(null=True, blank=True)
    action = models.CharField(max_length=10, choices=FEED_ACTIONS, null=True, blank=True)
    timestamp = models.DateTimeField(default=now, null=True, blank=True)  # Allow null and blank values

    def save(self, *args, **kwargs):
        if self.feed:  # Ensure feed exists before updating stock
            if self.action == 'ADD':
                self.feed.quantity_kg += self.quantity_kg or 0
            elif self.action == 'CONSUME':
                self.feed.quantity_kg -= self.quantity_kg or 0
            self.feed.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} {self.action.lower()} {self.quantity_kg} kg of {self.feed.name if self.feed else 'Unknown'} on {self.timestamp}"

