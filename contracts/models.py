from django.db import models

class Contract(models.Model):

    farmer_name = models.CharField(max_length=255)
    farm_code = models.CharField(max_length=50, unique=True)
    initial_setup_fee = models.DecimalField(max_digits=10, decimal_places=2, default=150000.00)
    downpayment = models.DecimalField(max_digits=10, decimal_places=2, default=75000.00)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    recurring_expenditure = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paybill_number = models.CharField(max_length=50, default="880100")
    account_number = models.CharField(max_length=50, default="302301")
    bank_account = models.CharField(max_length=50, default="1000614126")
    due_date = models.IntegerField(default=5)
    notice_period_months = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract for {self.farmer_name} ({self.farm_code})"

