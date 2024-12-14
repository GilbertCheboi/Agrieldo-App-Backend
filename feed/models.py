from django.conf import settings
from django.db import models

class Feed(models.Model):
    FEED_TYPES = [
        ('silage', 'Silage'),
        ('concentrates', 'Concentrates'),
        ('hay', 'Hay'),
        # Add other feed types if necessary
    ]

    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feeds')

    feed_type = models.CharField(max_length=20, choices=FEED_TYPES)
    date = models.DateField()
    starting_balance = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of feed at the beginning of the day
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of feed at the end of the day
    amount_added = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Feed added
    amount_consumed = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Feed consumed

    def save(self, *args, **kwargs):
        # Calculate closing balance as: starting balance + feed added - feed consumed
        self.closing_balance = self.starting_balance + self.amount_added - self.amount_consumed
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.farmer.username} - {self.feed_type} - {self.date}"

