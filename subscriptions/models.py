from django.db import models

from django.conf import settings

# Create your models here.
class Package(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per cow
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.package.name})"

class Subscription(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        null=True,  # Allow NULL for existing rows
    )
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='subscriptions')
    number_of_cows = models.PositiveIntegerField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_cost(self):
        return self.number_of_cows * self.package.price

    def __str__(self):
        return f"{self.package.name} - {self.number_of_cows} cows ({self.payment_status})"
