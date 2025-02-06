from django.contrib import admin
from .models import Animal, Dairy_Cow, Beef_Cow, Sheep, Goat, DairyMedicalRecord, BeefMedicalRecord, SheepMedicalRecord, GoatMedicalRecord

# Register the Animal model and its subclasses
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'age','tag', 'is_for_sale', 'price', 'gender', 'owner')
    search_fields = ('name', 'species', 'tag')
    list_filter = ('species', 'gender', 'image')

@admin.register(Dairy_Cow)
class DairyCowAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'milk_production', 'age', 'gender', 'owner')
    search_fields = ('name', 'breed')
    list_filter = ('breed','image')

@admin.register(Beef_Cow)
class BeefCowAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'weight', 'age', 'gender', 'owner')
    search_fields = ('name', 'breed')
    list_filter = ('breed', 'image')

@admin.register(Sheep)
class SheepAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'wool_yield', 'gender',  'owner')
    search_fields = ('name',)
    list_filter = ( 'image',)

@admin.register(Goat)
class GoatAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'meat_yield', 'gender', 'owner')
    search_fields = ('name',)
    list_filter = ( 'image',)

@admin.register(DairyMedicalRecord)
class DairyMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'diagnosis', 'veterinarian')
    search_fields = ('animal__name', 'diagnosis')
    list_filter = ('date', 'veterinarian')
@admin.register(BeefMedicalRecord)
class BeefMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'diagnosis', 'veterinarian')
    search_fields = ('animal__name', 'diagnosis')
    list_filter = ('date', 'veterinarian')

@admin.register(GoatMedicalRecord)
class GoatMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'diagnosis', 'veterinarian')
    search_fields = ('animal__name', 'diagnosis')
    list_filter = ('date', 'veterinarian')

@admin.register(SheepMedicalRecord)
class SheepMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'diagnosis', 'veterinarian')
    search_fields = ('animal__name', 'diagnosis')
    list_filter = ('date', 'veterinarian')

