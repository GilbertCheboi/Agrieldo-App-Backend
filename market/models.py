from django.db import models
from django.conf import settings
from animals.models import Animal  # make sure Animal model exists

def listing_image_upload_path(instance, filename):
    return f"market/listings/animal_{instance.animal.id}/{filename}"


class MarketListing(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('hidden', 'Hidden'),
    )

    animal = models.OneToOneField(
        Animal,
        on_delete=models.CASCADE,
        related_name="market_listing"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="market_sales"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    image = models.ImageField(
        upload_to=listing_image_upload_path,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.animal.name} - {self.status}"

