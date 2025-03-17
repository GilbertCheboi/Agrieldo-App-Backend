from django.db import models
from django.conf import settings


class Store(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stores'
    )
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Produce(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='produces'
    )
    name = models.CharField(max_length=50)
    total_quantity = models.FloatField(default=0)
    unit = models.CharField(max_length=10, default="kg")
    image = models.ImageField(upload_to='produce_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Outlet(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='outlets'
    )

    def __str__(self):
        return self.name


class Inventory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inventories'
    )
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, null=True, blank=True, on_delete=models.CASCADE, related_name='store_inventory')
    outlet = models.ForeignKey(Outlet, null=True, blank=True, on_delete=models.CASCADE, related_name='outlet_inventory')
    quantity = models.FloatField(default=0)
    created_at = models.DateTimeField(blank=True, null=True)  # ✅ Add this line

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('produce', 'store', 'outlet')

    def __str__(self):
        location = self.store.name if self.store else (self.outlet.name if self.outlet else "Unknown")
        return f"{self.produce.name} at {location}"

class Transaction(models.Model):
    TYPE_CHOICES = (
        ('ADD_TO_STORE', 'Add to Store'),
        ('STORE_TO_OUTLET', 'Store to Outlet'),
        ('OUTLET_TRANSFER', 'Outlet to Outlet'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE)
    quantity = models.FloatField()
    store = models.ForeignKey(Store, null=True, blank=True, on_delete=models.CASCADE)
    source_outlet = models.ForeignKey(Outlet, null=True, blank=True, related_name='source_transactions', on_delete=models.CASCADE)
    destination_outlet = models.ForeignKey(Outlet, null=True, blank=True, related_name='destination_transactions', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update Produce total_quantity and Inventory
        if self.transaction_type == 'ADD_TO_STORE':
            # Increase total quantity
            self.produce.total_quantity += self.quantity
            self.produce.save()

            # Update store inventory
            inventory, _ = Inventory.objects.get_or_create(
                user=self.user,
                produce=self.produce,
                store=self.store,
                outlet=None
            )
            inventory.quantity += self.quantity
            inventory.save()

        elif self.transaction_type == 'STORE_TO_OUTLET':
            # Reduce store inventory
            store_inventory = Inventory.objects.get(
                user=self.user,
                produce=self.produce,
                store=self.store,
                outlet=None
            )
            store_inventory.quantity -= self.quantity
            store_inventory.save()

            # Add to outlet inventory
            outlet_inventory, _ = Inventory.objects.get_or_create(
                user=self.user,
                produce=self.produce,
                store=None,
                outlet=self.destination_outlet
            )
            outlet_inventory.quantity += self.quantity
            outlet_inventory.save()

        elif self.transaction_type == 'OUTLET_TRANSFER':
            # Move quantity between outlets
            source_inventory = Inventory.objects.get(
                user=self.user,
                produce=self.produce,
                store=None,
                outlet=self.source_outlet
            )
            source_inventory.quantity -= self.quantity
            source_inventory.save()

            dest_inventory, _ = Inventory.objects.get_or_create(
                user=self.user,
                produce=self.produce,
                store=None,
                outlet=self.destination_outlet
            )
            dest_inventory.quantity += self.quantity
            dest_inventory.save()

    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} {self.produce.unit} of {self.produce.name} on {self.timestamp}"

