from django.db import models
from django.conf import settings

class Machinery(models.Model):
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField()
    condition = models.CharField(
        max_length=100,
        choices=[('New', 'New'), ('Used', 'Used'), ('Needs Repair', 'Needs Repair')]
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_machinery'
    )  # Farm owner
    image = models.ImageField(upload_to='machinery_images/', blank=True, null=True)  # New field

    def __str__(self):
        return self.name

class MachineryUsageLog(models.Model):
    machinery = models.ForeignKey(Machinery, on_delete=models.CASCADE, related_name="usage_logs")
    usage_date = models.DateField()
    hours_used = models.DecimalField(max_digits=5, decimal_places=2)
    operator = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    fuel_consumed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machinery.name} - {self.usage_date}"

class MaintenanceLog(models.Model):
    machinery = models.ForeignKey(Machinery, on_delete=models.CASCADE, related_name='maintenance_logs')
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    next_maintenance_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.machinery.name} - {self.date}"

class FuelLog(models.Model):
    machinery = models.ForeignKey(Machinery, on_delete=models.CASCADE, related_name='fuel_logs')
    liters = models.FloatField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.machinery.name} - {self.liters}L"

class SparePart(models.Model):
    machinery = models.ForeignKey(Machinery, on_delete=models.CASCADE, related_name='spare_parts')
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    def __str__(self):
        return f"{self.name} for {self.machinery.name}"

class Alert(models.Model):
    machinery = models.ForeignKey(Machinery, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=100, choices=[('Maintenance', 'Maintenance'), ('Fuel', 'Fuel')])
    threshold = models.FloatField()  # Custom threshold set by the user
    notified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.alert_type} Alert for {self.machinery.name}"

