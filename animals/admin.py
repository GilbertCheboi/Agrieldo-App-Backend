# animals/admin.py
from django.contrib import admin
from .models import (
    Animal, AnimalImage, HealthRecord, ProductionData, ReproductiveHistory,
    FeedManagement, FinancialDetails, LactationStatus, LifetimeStats
)

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('tag', 'name', 'breed', 'gender', 'farm', 'owner', 'assigned_worker')
    list_filter = ('breed', 'gender', 'farm')
    search_fields = ('tag', 'name', 'breed', 'farm__farm_id', 'owner', 'assigned_worker')

@admin.register(AnimalImage)
class AnimalImageAdmin(admin.ModelAdmin):
    list_display = ('animal', 'image', 'caption')
    list_filter = ('animal',)
    search_fields = ('animal__tag', 'caption')


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'type', 'details', 'clinical_signs', 'diagnosis', 'treatment')  # Updated
    list_filter = ('date', 'type', 'is_sick')  # Optionally added 'is_sick'
    search_fields = ('animal__tag', 'type', 'details', 'clinical_signs', 'diagnosis', 'treatment')  # Updated
    date_hierarchy = 'date'


@admin.register(ProductionData)
class ProductionDataAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'session', 'milk_yield', 'feed_consumption', 'scc', 'fat_percentage', 'protein_percentage')
    list_filter = ('date', 'session')
    search_fields = ('animal__tag',)
    date_hierarchy = 'date'


@admin.register(ReproductiveHistory)
class ReproductiveHistoryAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'event', 'details')
    list_filter = ('event', 'date')
    search_fields = ('animal__tag', 'event', 'details')
    date_hierarchy = 'date'

@admin.register(FeedManagement)
class FeedManagementAdmin(admin.ModelAdmin):
    list_display = ('animal', 'date', 'type', 'quantity')
    list_filter = ('date', 'type')
    search_fields = ('animal__tag', 'type', 'quantity')
    date_hierarchy = 'date'

@admin.register(FinancialDetails)
class FinancialDetailsAdmin(admin.ModelAdmin):
    list_display = ('animal', 'total_feed_cost', 'total_vet_cost', 'total_breeding_cost', 'total_revenue_from_milk', 'total_cost')

@admin.register(LactationStatus)
class LactationStatusAdmin(admin.ModelAdmin):
    list_display = ('animal', 'lactation_number', 'days_in_milk', 'is_milking')
    list_filter = ('is_milking',)
    search_fields = ('animal__tag',)

@admin.register(LifetimeStats)
class LifetimeStatsAdmin(admin.ModelAdmin):
    list_display = ('animal', 'total_milk', 'avg_yield', 'calves')
    search_fields = ('animal__tag',)

