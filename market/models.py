from django.db import models
from animals.models import Animal

class Auction(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, null=True, blank=True)
    listed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    auction_end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Auction for {self.animal.name} ({self.animal.species})"

