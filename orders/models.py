from django.db import models


class UnifiedOrder(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    mpesa_checkout_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UnifiedOrder #{self.id} - {self.customer_name}"


class UnifiedOrderItem(models.Model):
    unified_order = models.ForeignKey("orders.UnifiedOrder", on_delete=models.CASCADE, related_name="items")
    feed_order = models.ForeignKey("feed_store.FeedOrder", null=True, blank=True, on_delete=models.SET_NULL)
    drug_order = models.ForeignKey("drug_store.DrugOrder", null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Item #{self.id} of Unified #{self.unified_order.id}"

