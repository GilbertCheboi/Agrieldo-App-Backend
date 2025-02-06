from django.db import models
from django.conf import settings
from farms.models import Farm


class Animal(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown'),
    ]

    # Fields for the naming convention
    farm_name = models.CharField(max_length=50, blank=True, null=True)
    family_line = models.CharField(max_length=10, blank=True, null=True)
    generation = models.CharField(max_length=10, blank=True, null=True)
    serial_number = models.PositiveIntegerField(blank=True, null=True)
    year_of_birth = models.PositiveIntegerField(blank=True, null=True)

    # Additional animal details
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    is_for_sale = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animals')
    image = models.ImageField(upload_to='animals/', blank=True, null=True)  # New image field
    age = models.PositiveIntegerField()

    # Automatically generate the tag_name based on the naming convention
    @property
    def tag(self):
        return f"{self.farm_name}-{self.family_line}-G{self.generation}-" \
               f"{str(self.serial_number).zfill(3)}-{self.year_of_birth}"

    def __str__(self):
        return f"{self.name} ({self.species}) - {self.tag}"

class Dairy_Cow(Animal):
    breed = models.CharField(max_length=100, blank=True, null=True)
    milk_production = models.FloatField(null=True, blank=True)  # in liters

    def __str__(self):
        return f"Cow: {self.name} (Breed: {self.breed})"

class Beef_Cow(Animal):
    breed = models.CharField(max_length=100, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)  # in kgs

    def __str__(self):
        return f"Cow: {self.name} (Breed: {self.breed})"

# Model for Sheep
class Sheep(Animal):
    wool_yield = models.FloatField(blank=True, null=True)  # in kilograms
    twin = models.BooleanField(default=False)

    def __str__(self):
        return f"Sheep: {self.name} (Wool yield: {self.wool_yield} kg)"

# Model for Goats
class Goat(Animal):
    meat_yield = models.FloatField()  # in kilograms

    def __str__(self):
        return f"Goat: {self.name} (Meat yield: {self.meat_yield} kg)"

class SheepMedicalRecord(models.Model):
    animal = models.ForeignKey(Sheep, on_delete=models.CASCADE, related_name='sheep_medical_records')
    date = models.DateField(auto_now_add=True)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    veterinarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sheep_medical_records')
    
    def __str__(self):
        return f"Medical Record for {self.animal.name} on {self.date}"

class DairyMedicalRecord(models.Model):
    animal = models.ForeignKey(Dairy_Cow, on_delete=models.CASCADE, related_name='dairy_medical_records')
    date = models.DateField(auto_now_add=True)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    veterinarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dairy_medical_records')
    
    def __str__(self):
        return f"Medical Record for {self.animal.name} on {self.date}"
class BeefMedicalRecord(models.Model):
    animal = models.ForeignKey(Beef_Cow, on_delete=models.CASCADE, related_name='beef_medical_records')
    date = models.DateField(auto_now_add=True)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    veterinarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='beef_medical_records')
    
    def __str__(self):
        return f"Medical Record for {self.animal.name} on {self.date}"
class GoatMedicalRecord(models.Model):
    animal = models.ForeignKey(Goat, on_delete=models.CASCADE, related_name='goat_medical_records')
    date = models.DateField(auto_now_add=True)
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    veterinarian = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goat_medical_records')
    
    def __str__(self):
        return f"Medical Record for {self.animal.name} on {self.date}"



class AnimalGallery(models.Model):
    animal = models.ForeignKey(Animal, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='animals/gallery/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image for {self.animal.name} ({self.created_at})"
