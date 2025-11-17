from django.db import models

class DrugCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Drug(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(DrugCategory, on_delete=models.CASCADE, related_name='drugs')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    usage_instructions = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='drug_products/', blank=True, null=True)  # 👈 NEW
    created_at = models.DateTimeField(auto_now_add=True)



class DrugOrder(models.Model):
    customer_name = models.CharField(max_length=200)
    customer_contact = models.CharField(max_length=15)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"
