from django.db import models
from django.utils.timezone import now
from django.conf import settings
from farms.models import Farm  # ✅ Import Farm from your farms app


class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='feed_stores')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_stores',  # 👈 changed from 'stores' to 'feed_stores'
        null =True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'farm')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.farm.name})"
class Feed(models.Model):
    """
    Represents a feed item (e.g., Hay, Silage, Dairy Meal) stored in a specific farm store.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
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
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='feeds',
        null=True,
        blank=True,
        help_text="Store where this feed is kept"
    )

    class Meta:
        unique_together = ('name', 'owner', 'store')  # Same feed can exist in different stores

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
        return f"{self.name} - {self.quantity_kg} kg ({self.store.name if self.store else 'No Store'})"


class FeedingPlan(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, help_text="Name of the feeding plan (e.g., 'Lactating Cow Plan')")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeding_plans',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'name')

    def __str__(self):
        return self.name


class FeedingPlanItem(models.Model):
    plan = models.ForeignKey(FeedingPlan, on_delete=models.CASCADE, related_name='items')
    feed = models.ForeignKey('Feed', on_delete=models.CASCADE)
    quantity_per_animal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity of this feed (in kg) per animal."
    )

    class Meta:
        unique_together = ('plan', 'feed')

    def __str__(self):
        return f"{self.feed.name}: {self.quantity_per_animal} kg"

