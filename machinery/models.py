from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Machinery(models.Model):
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255, blank=True, null=True)
    purchase_date = models.DateField()
    is_available = models.BooleanField(default=True) 
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

class MachineryVendorApplication(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,        # ← allow null for now
        blank=True,
        on_delete=models.CASCADE,
        related_name='vendor_app',
    )
    MACHINE_TYPES = [
        ('TRACTOR', 'Tractor'),
        ('HARVESTER', 'Harvester'),
        ('PLOUGH', 'Plough'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    type_of_machine = models.CharField(max_length=20, choices=MACHINE_TYPES)
    model = models.CharField(max_length=255)
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Rate charged per day in your local currency"
    )
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.type_of_machine} ({self.model})"
        
class MachineryOrder(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='machinery_orders_as_vendor')
    machinery = models.ForeignKey(MachineryVendorApplication, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    land_size_acres = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
