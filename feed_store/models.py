from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FeedProduct(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='feed_products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FeedOrder(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    )

    customer_name = models.CharField(max_length=200)
    customer_contact = models.CharField(max_length=15)
    product = models.ForeignKey(FeedProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    mpesa_receipt = models.CharField(max_length=50, null=True, blank=True)

    order_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total price
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"FeedOrder #{self.id} - {self.customer_name}"

