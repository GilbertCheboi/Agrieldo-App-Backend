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
    Both farm owners and staff can add or top up feed in the same store.
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
        blank=True,
        help_text="User who created the feed record"
    )

    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        related_name='feeds',
        null=True,
        blank=True,
        help_text="Store where this feed is kept"
    )

    # ✅ Audit trail fields
    last_topped_up_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='topped_up_feeds',
        help_text="Last user who topped up this feed"
    )
    last_topped_up_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ✅ Remove owner from uniqueness to allow shared feed per store
        unique_together = ('name', 'store')

    def __str__(self):
        return f"{self.name} - {self.quantity_kg} kg ({self.store.name if self.store else 'No Store'})"

    # ✅ Deduct quantity safely
    def deduct_feed(self, quantity):
        """Deduct quantity from the feed if there is enough stock."""
        if self.quantity_kg >= quantity:
            self.quantity_kg -= quantity
            self.save()
            return True
        return False

    # ✅ Add feed with audit tracking
    def add_feed(self, quantity, price_per_kg=None, user=None):
        """Add quantity to existing feed, optionally update price_per_kg and track who topped up."""
        quantity = float(quantity)
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        self.quantity_kg += quantity

        if price_per_kg is not None:
            price_per_kg = float(price_per_kg)
            if price_per_kg < 0:
                raise ValueError("Price cannot be negative")
            self.price_per_kg = price_per_kg

        if user:
            self.last_topped_up_by = user

        self.save()
        return True





class FeedingPlan(models.Model):
    """
    Represents a feeding plan (e.g., 'Lactating Cow Plan') for a specific store.
    Both farm owner and staff can create/manage plans for their store.
    """
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of the feeding plan (e.g., 'Lactating Cow Plan')"
    )

    store = models.ForeignKey(
        'Store',
        on_delete=models.CASCADE,
        related_name='feeding_plans',
        help_text="Store this feeding plan belongs to",
        blank = True,
        null = True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeding_plans_created',
        help_text="User who created this feeding plan"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feeding_plans_updated',
        help_text="Last user who modified this feeding plan"
    )

    class Meta:
        unique_together = ('store', 'name')  # Unique per store, not per owner
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.store.name})"


class FeedingPlanItem(models.Model):
    """
    Links feeds to a feeding plan, defining how much of each feed type
    is allocated per animal.
    """
    plan = models.ForeignKey(
        FeedingPlan,
        on_delete=models.CASCADE,
        related_name='items'
    )

    feed = models.ForeignKey(
        'Feed',
        on_delete=models.CASCADE,
        related_name='feeding_plan_items',
        help_text="Feed used in this plan"
    )

    quantity_per_animal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity of this feed (in kg) per animal."
    )

    class Meta:
        unique_together = ('plan', 'feed')
        ordering = ['feed__name']

    def __str__(self):
        return f"{self.feed.name}: {self.quantity_per_animal} kg"

