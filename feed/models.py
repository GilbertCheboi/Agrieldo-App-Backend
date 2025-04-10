from django.db import models
from django.utils.timezone import now
from django.conf import settings

class Feed(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)  # Removed unique=True
    quantity_kg = models.FloatField(default=0.0, null=True, blank=True)
    price_per_kg = models.FloatField(default=0.0, help_text="Cost per kg")
    created_at = models.DateTimeField(default=now, null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeds',
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('name', 'owner')

    def deduct_feed(self, quantity):
        """Deduct quantity from the feed if there is enough stock."""
        if self.quantity_kg >= quantity:
            self.quantity_kg -= quantity
            self.save()
            return True
        return False

    def add_feed(self, quantity, price_per_kg=None):
        """Add quantity to existing feed, optionally update price_per_kg."""
        quantity = float(quantity)
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity_kg += quantity
        if price_per_kg is not None:
            price_per_kg = float(price_per_kg)
            if price_per_kg < 0:
                raise ValueError("Price cannot be negative")
            self.price_per_kg = price_per_kg
        self.save()
        return True

    def __str__(self):
        return f"{self.name} - {self.quantity_kg} kg"
