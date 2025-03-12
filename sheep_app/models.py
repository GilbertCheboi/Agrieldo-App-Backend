# sheep_app/models.py
from django.db import models
from farms.models import Farm

class SheepType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Merino, Suffolk
    description = models.TextField(blank=True)           # Breed characteristics
    avg_wool_yield = models.FloatField(default=0.0)      # kg, expected average
    avg_weight = models.FloatField(default=0.0)          # kg, expected average

    def __str__(self):
        return self.name

class Sheep(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="sheep")
    sheep_type = models.ForeignKey(SheepType, on_delete=models.SET_NULL, null=True, related_name="sheep")
    tag_number = models.CharField(max_length=50, unique=True)
    dob = models.DateField()

    def __str__(self):
        return f"{self.tag_number} - {self.farm.name} ({self.sheep_type.name if self.sheep_type else 'Unknown'})"

class SheepHealthRecord(models.Model):
    sheep = models.ForeignKey(Sheep, on_delete=models.CASCADE, related_name="health_records")
    date = models.DateField(auto_now_add=True)
    is_sick = models.BooleanField(default=False)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)

    def __str__(self):
        return f"Health Record for {self.sheep.tag_number} - {self.date}"

class SheepReproduction(models.Model):
    sheep = models.ForeignKey(Sheep, on_delete=models.CASCADE, related_name="reproduction_records")
    mating_date = models.DateField()
    partner_tag = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    offspring_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Reproduction for {self.sheep.tag_number} - {self.mating_date}"

class SheepProduction(models.Model):
    sheep = models.ForeignKey(Sheep, on_delete=models.CASCADE, related_name="production_records")
    date = models.DateField(auto_now_add=True)
    wool_yield = models.FloatField(default=0.0)  # kg
    weight = models.FloatField(default=0.0)      # kg, live weight
    shearing_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Production for {self.sheep.tag_number} - {self.date}"

class SheepImage(models.Model):
    sheep = models.ForeignKey(Sheep, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='sheep_images/', blank=True, null=True)
    upload_date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.sheep.tag_number} - {self.upload_date}"
