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
import logging


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
        """
        Categorizes the animal based on its age, reproductive status, and lactation status.
        """
        # Calculate age in months
        age_months = (timezone.now().date() - self.dob).days / 30
        print(f"Debug: {self.tag} - Age in months: {age_months}")

        # Get latest lactation and reproductive event
        latest_lactation = self.lactation_periods.order_by('-last_calving_date').first() if self.lactation_periods.exists() else None
        latest_repro_event = self.reproductive_history.order_by('-date').first() if self.reproductive_history.exists() else None

        # Debugging
        print(f"Debug: {self.tag} - Latest Lactation: {latest_lactation}")
        print(f"Debug: {self.tag} - Latest Reproductive Event: {latest_repro_event}")

        # Males
        if self.gender == "Male":
            return "Bull"

        # Young Female Stages
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

        # Prioritize Lactation Status Over Pregnancy
        if latest_lactation and latest_lactation.is_milking:
            dim = latest_lactation.days_in_milk
            print(f"Debug: {self.tag} - Milking: {latest_lactation.is_milking}, DIM: {dim}")

            if dim <= 100:
                return "Early Lactating"
            elif 101 <= dim <= 200:
                return "Mid Lactating"
            else:
                return "Late Lactating"

        # Pregnancy Status
        if latest_repro_event and self.is_pregnant:
            if latest_lactation and latest_lactation.expected_calving_date:
                days_to_calving = (latest_lactation.expected_calving_date - timezone.now().date()).days
                print(f"Debug: {self.tag} - Days to Calving: {days_to_calving}")

                if 0 < days_to_calving <= 30:
                    return "Steaming"  # Close to calving
            return "In-Calf"

        # Default to Heifer if no other category fits
        return "Heifer"

    @property
    def is_pregnant(self):
        """
        Determines if the animal is pregnant by checking its reproductive history.
        """
        if not self.reproductive_history.exists():
            return False
        latest_event = self.reproductive_history.order_by('-date').first()
        print(f"Debug: {self.tag} - Latest reproductive event: {latest_event.date} - {latest_event.event}")

        if latest_event.event in ["AI", "Natural Breeding"]:
            calving_after = self.reproductive_history.filter(
                event="Calving",
                date__gt=latest_event.date
            ).exists()
            print(f"Debug: {self.tag} - Calving after last breeding: {calving_after}")
            return not calving_after
        return False

    @property
    def is_sick(self):
        """
        Checks if the animal has been marked as sick within the last 30 days.
        """
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
    milk_price_per_liter = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))  # New field

    feed_consumption = models.FloatField(blank= True, null=True)
    scc = models.IntegerField(blank=True, null=True)
    fat_percentage = models.FloatField(null=True, blank=True)
    protein_percentage = models.FloatField(blank=True, null=True)

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
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_unit = models.FloatField(default=0.0, help_text="Cost per kg of feed")
    total_cost = models.FloatField(default=0.0, help_text="Total cost for this feed entry (quantity * cost_per_unit)")

    def save(self, *args, **kwargs):
        # Convert quantity to float for multiplication with cost_per_unit
        self.total_cost = float(self.quantity) * self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.type}"

class FinancialDetails(models.Model):
    animal = models.OneToOneField('Animal', on_delete=models.CASCADE, related_name="financial_details")
    total_feed_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_vet_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_breeding_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_revenue_from_milk = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))


@receiver(post_save, sender=Animal)
def create_financial_details(sender, instance, created, **kwargs):
    if created:
        FinancialDetails.objects.get_or_create(animal=instance)

@receiver(post_save, sender=HealthRecord)
def update_financial_details_health(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        cost = Decimal(str(instance.cost))  # Convert float to Decimal
        financial.total_vet_cost += cost
        financial.total_cost += cost
        financial.save()  
@receiver(post_save, sender=ReproductiveHistory)
def update_financial_details_reproduction(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        if instance.event in ["AI", "Natural Breeding"]:
            cost = Decimal(str(instance.cost))  # Convert float to Decimal
            financial.total_breeding_cost += cost
            financial.total_cost += cost
        financial.save()

logger = logging.getLogger(__name__)

@receiver(post_save, sender='animals.FeedManagement')
def update_financial_details_feed(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        total_cost = Decimal(f'{instance.total_cost:.2f}')  # float to Decimal
        logger.info(f"total_cost: {total_cost}, type: {type(total_cost)}")
        logger.info(f"total_feed_cost: {financial.total_feed_cost}, type: {type(financial.total_feed_cost)}")
        # Ensure total_feed_cost is Decimal
        if not isinstance(financial.total_feed_cost, Decimal):
            financial.total_feed_cost = Decimal(f'{float(financial.total_feed_cost):.2f}')
        if not isinstance(financial.total_cost, Decimal):
            financial.total_cost = Decimal(f'{float(financial.total_cost):.2f}')
        financial.total_feed_cost += total_cost
        financial.total_cost += total_cost
        financial.save()

@receiver(post_save, sender=ProductionData)
def update_financial_details_milk(sender, instance, created, **kwargs):
    if created:
        financial, _ = FinancialDetails.objects.get_or_create(animal=instance.animal)
        revenue = Decimal(instance.milk_yield) * instance.milk_price_per_liter  # Calculate revenue
        financial.total_revenue_from_milk += revenue
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
