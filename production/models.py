# production/models.py
from django.db import models
from django.conf import settings
from animals.models import Animal
from farms.models import Farm  # Import the Farm model
from datetime import date

class Production(models.Model):
    PRODUCTION_TYPES = [
        ('milk', 'Milk'),
        ('eggs', 'Eggs'),
        ('wool', 'Wool'),
        # Add more production types as necessary
    ]

    SESSION_TYPES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        # Add more session types as necessary
    ]

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='productions'
    )
    production_type = models.CharField(max_length=20, choices=PRODUCTION_TYPES)
    session = models.CharField(max_length=20, choices=SESSION_TYPES, default='Morning')
    date = models.DateField()
    output = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='productions', null=True, blank=True)

    def __str__(self):
        return f"{self.farmer.username} - {self.production_type} - {self.date} - {self.animal.name if self.animal else 'No Animal'}"



class ProductionRecord(models.Model):
    COMMODITY_CHOICES = [
        ("Tomatoes", "Tomatoes"),
        ("Onions", "Onions"),
        ("Cabbage", "Cabbage"),
        ("Kales", "Kales"),
        ("Milk", "Milk"),
        ("Potatoes", "Potatoes"),
    ]
    
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='production_records'
    )
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name='production_records',
        null=True, blank=True
    )  # Associate production with a farm
    commodity = models.CharField(max_length=50, choices=COMMODITY_CHOICES)
    quantity = models.CharField(max_length=50)  # Example: '500 kg', '200 liters'
    last_updated = models.DateField(auto_now=True)  # Updates whenever the record is modified
    created_at = models.DateField(default=date.today)

    def __str__(self):
        farm_name = self.farm.name if self.farm else "No Farm"
        return f"{self.commodity} - {self.quantity} ({farm_name})"
