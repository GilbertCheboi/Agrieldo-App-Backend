from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    auction_end_date = models.DateField(null=True, blank=True)
    #image = models.imageField(null=True, blank=True)
    #video = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.name


class Auction(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    auction_end_date = models.DateField(null=True, blank=True)
    
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
