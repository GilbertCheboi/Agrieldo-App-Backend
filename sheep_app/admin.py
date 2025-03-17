# sheep_app/admin.py
from django.contrib import admin
from .models import (
    Sheep,
    SheepType,
    SheepHealthRecord,
    SheepReproduction,
    SheepProduction,
    SheepImage,
)

# Register SheepType
@admin.register(SheepType)
class SheepTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'avg_wool_yield', 'avg_weight')
    search_fields = ('name',)
    list_filter = ('avg_wool_yield', 'avg_weight')
    ordering = ('name',)

# Register Sheep
@admin.register(Sheep)
class SheepAdmin(admin.ModelAdmin):
    list_display = ('tag_number', 'farm', 'sheep_type', 'dob')
    list_filter = ('farm', 'sheep_type', 'dob')
    search_fields = ('tag_number', 'farm__name', 'sheep_type__name')
    ordering = ('tag_number',)
    list_select_related = ('farm', 'sheep_type')  # Optimize queries

# Register SheepHealthRecord
@admin.register(SheepHealthRecord)
class SheepHealthRecordAdmin(admin.ModelAdmin):
    list_display = ('sheep', 'date', 'is_sick', 'diagnosis_short')
    list_filter = ('is_sick', 'date')
    search_fields = ('sheep__tag_number', 'diagnosis', 'treatment')
    ordering = ('-date',)

    def diagnosis_short(self, obj):
        return obj.diagnosis[:50] + ('...' if len(obj.diagnosis) > 50 else '')
    diagnosis_short.short_description = 'Diagnosis'

# Register SheepReproduction
@admin.register(SheepReproduction)
class SheepReproductionAdmin(admin.ModelAdmin):
    list_display = ('sheep', 'mating_date', 'birth_date', 'offspring_count')
    list_filter = ('mating_date', 'birth_date')
    search_fields = ('sheep__tag_number', 'partner_tag')
    ordering = ('-mating_date',)

# Register SheepProduction
@admin.register(SheepProduction)
class SheepProductionAdmin(admin.ModelAdmin):
    list_display = ('sheep', 'date', 'wool_yield', 'weight', 'shearing_date')
    list_filter = ('date', 'shearing_date')
    search_fields = ('sheep__tag_number',)
    ordering = ('-date',)

# Register SheepImage
@admin.register(SheepImage)
class SheepImageAdmin(admin.ModelAdmin):
    list_display = ('sheep', 'upload_date', 'description_short', 'image')
    list_filter = ('upload_date',)
    search_fields = ('sheep__tag_number', 'description')
    ordering = ('-upload_date',)

    def description_short(self, obj):
        return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
    description_short.short_description = 'Description'
