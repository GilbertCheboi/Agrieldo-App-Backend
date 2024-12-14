from django.db import models
from accounts.models import User

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"Invoice for {self.user.username} - {self.amount}"
