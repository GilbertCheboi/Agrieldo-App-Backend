# animals/models.py
from django.db import models
from datetime import timedelta
from farms.models import Farm  # Import Farm from farms app
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from decimal import Decimal


class Animal(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    breed = models.CharField(max_length=50)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    farm = models.ForeignKey('farms.Farm', on_delete=models.CASCADE, related_name='animals')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='animals_profile'
    )
    assigned_worker = models.CharField(max_length=100)

    def __str__(self):
        return self.tag

    def category(self):
        # Calculate age in months
        age_months = (timezone.now().date() - self.dob).days / 30

        # Get the latest lactation period (if any)
        latest_lactation = self.lactation_periods.order_by('-last_calving_date').first() if self.lactation_periods.exists() else None

        # Get the latest reproductive event
        repro_history = self.reproductive_history.order_by('-date').first() if self.reproductive_history.exists() else None

        # Male animals
        if self.gender == "Male":
            return "Bull"

        # Age-based categories for young females
        if age_months < 3:
            return "Calf (0-3 months)"
        elif 3 <= age_months < 6:
            return "Weaner Stage 1 (3-6 months)"
        elif 6 <= age_months < 9:
            return "Weaner Stage 2 (6-9 months)"
        elif 9 <= age_months < 12:
            return "Yearling (9-12 months)"
        elif 12 <= age_months < 15:
            return "Bulling (12-15 months)"

        # Beyond 15 months, use reproductive and lactation status
        if repro_history and self.is_pregnant:
            if latest_lactation and latest_lactation.expected_calving_date:
                days_to_calving = (latest_lactation.expected_calving_date - timezone.now().date()).days
                if 0 < days_to_calving <= 30:
                    return "Steaming"  # One month before calving
            return "In-Calf"  # Pregnant but not near calving

        # Lactation-based categories
        if latest_lactation:
            if latest_lactation.lactation_number == 0:  # Rare edge case
                return "Heifer"
            elif latest_lactation.is_milking:
                dim = latest_lactation.days_in_milk
                if dim <= 100:
                    return "Early Lactating"
                elif 101 <= dim <= 200:
                    return "Mid Lactating"
                else:  # dim > 200
                    return "Late Lactating"
            else:
                return "Dry"

        # Default for females over 15 months with no lactation or pregnancy
        return "Heifer"

    @property
    def is_pregnant(self):
        if not self.reproductive_history.exists():
            return False
        latest_event = self.reproductive_history.order_by('-date').first()
        if latest_event.event in ["AI", "Natural Breeding"]:  # Adjust if using is_pregnancy_start
            calving_after = self.reproductive_history.filter(
                event="Calving",
                date__gt=latest_event.date
            ).exists()
            return not calving_after
        return False

    @property
    def is_sick(self):
        recent_threshold = timezone.now().date() - timedelta(days=30)
        return self.health_records.filter(
            is_sick=True,
            date__gte=recent_threshold
        ).exists()



class AnimalImage(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='animal_images/', null=True, blank=True)

    caption = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.animal.tag}"



class HealthRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    date = models.DateField()
    type = models.CharField(max_length=50)
    details = models.TextField()
    is_sick = models.BooleanField(default=False)
    clinical_signs = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    cost = models.FloatField(default=0.0, help_text="Cost of this health record (e.g., vet fees, medication)")  # New field

    def __str__(self):
        return f"{self.date} - {self.type}"

class ProductionData(models.Model):
    # Define session choices as a tuple of tuples
    SESSION_CHOICES = (
        ('MORNING', 'Morning'),
        ('AFTERNOON', 'Afternoon'),
        ('EVENING', 'Evening'),
    )
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='production_data')
    date = models.DateField()
    session = models.CharField(max_length=10, choices=SESSION_CHOICES, default='MORNING')
    milk_yield = models.FloatField()
    feed_consumption = models.FloatField()
    scc = models.IntegerField()
    fat_percentage = models.FloatField()
    protein_percentage = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.session} - {self.milk_yield}L"


class ReproductiveHistory(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='reproductive_history')
    date = models.DateField()
    event = models.CharField(max_length=50)
    details = models.TextField(blank=True, null=True)
    cost = models.FloatField(default=0.0, help_text="Cost of this reproductive event (e.g., AI fees, breeding fees)")  # New field

    def __str__(self):
        return f"{self.date} - {self.event}"

    @property
    def is_pregnancy_start(self):
        return self.event in ["AI", "Natural Breeding"]

    @property
    def expected_calving_date(self):
        if self.is_pregnancy_start:
            return self.date + timedelta(days=280)
        return None


class FeedManagement(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='feed_management')
    date = models.DateField()
    type = models.CharField(max_length=50)
    quantity = models.FloatField(help_text="Quantity of feed in kg")  # Changed to FloatField for precision
    cost_per_unit = models.FloatField(default=0.0, help_text="Cost per kg of feed")  # New field
    total_cost = models.FloatField(default=0.0, help_text="Total cost for this feed entry (quantity * cost_per_unit)")  # New field

    def save(self, *args, **kwargs):
        # Automatically calculate total_cost before saving
        self.total_cost = self.quantity * self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.type}"


class FinancialDetails(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, related_name="financial_details")
    total_feed_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_vet_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_breeding_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_revenue_from_milk = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

@receiver(post_save, sender=Animal)
def create_financial_details(sender, instance, created, **kwargs):
    if created:
        FinancialDetails.objects.get_or_create(animal=instance)

@receiver(post_save, sender=HealthRecord)
def update_financial_details_health(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        financial.total_vet_cost += Decimal(str(instance.cost))  # Convert to Decimal
        financial.total_cost += Decimal(str(instance.cost))      # Convert to Decimal
        financial.save()

@receiver(post_save, sender=ReproductiveHistory)
def update_financial_details_reproduction(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        if instance.event in ["AI", "Natural Breeding"]:
            financial.total_breeding_cost += Decimal(str(instance.cost))  # Convert to Decimal
            financial.total_cost += Decimal(str(instance.cost))           # Convert to Decimal
        financial.save()
@receiver(post_save, sender=FeedManagement)
def update_financial_details_feed(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        financial.total_feed_cost += Decimal(str(instance.total_cost))  # Use total_cost from FeedManagement
        financial.total_cost += Decimal(str(instance.total_cost))
        financial.save()

class LactationPeriod(models.Model):  # Renamed for clarity
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, related_name='lactation_periods')
    lactation_number = models.IntegerField()
    last_calving_date = models.DateField()  # Date of calving that started this period
    days_in_milk = models.IntegerField(editable=False)  # Computed from last_calving_date
    is_milking = models.BooleanField(default=True)
    expected_calving_date = models.DateField(null=True, blank=True)  # EDC for next calving
    end_date = models.DateField(null=True, blank=True)  # When this lactation period ends (optional)

    def save(self, *args, **kwargs):
        # Update days_in_milk from last_calving_date
        if self.last_calving_date:
            self.days_in_milk = (timezone.now().date() - self.last_calving_date).days
        else:
            self.days_in_milk = 0

        # Update expected_calving_date from latest breeding after this calving
        latest_breeding = self.animal.reproductive_history.filter(
            event__in=["AI", "Natural Breeding"],
            date__gt=self.last_calving_date
        ).order_by('-date').first()
        if latest_breeding and not self.animal.reproductive_history.filter(
            event="Calving", date__gt=latest_breeding.date
        ).exists():
            self.expected_calving_date = latest_breeding.date + timedelta(days=280)
        else:
            self.expected_calving_date = None

        # Set is_milking to False if within 60 days of expected calving
        if self.expected_calving_date:
            days_to_calving = (self.expected_calving_date - timezone.now().date()).days
            if days_to_calving <= 60 and self.is_milking:
                self.is_milking = False
            elif days_to_calving > 60 and not self.is_milking:
                self.is_milking = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Lactation {self.lactation_number} - {self.days_in_milk} DIM for {self.animal.tag}"

    @property
    def current_days_in_milk(self):
        if self.last_calving_date:
            return (timezone.now().date() - self.last_calving_date).days

class LifetimeStats(models.Model):
    animal = models.OneToOneField(Animal, on_delete=models.CASCADE, related_name='lifetime_stats')
    total_milk = models.FloatField()
    avg_yield = models.FloatField()
    calves = models.IntegerField()

    def __str__(self):
        return f"Lifetime Statsefor {self.animal.tag}"
        fields = ['lactation_number', 'days_in_milk', 'is_milking']
