from django.contrib import admin
from .models import Production, ProductionRecord

class ProductionAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('farmer', 'production_type', 'session', 'date', 'output', 'remarks', 'animal')
    
    # Fields to filter by
    list_filter = ('production_type', 'session', 'date', 'animal')
    
    # Fields to search
    search_fields = ('farmer__username', 'production_type', 'animal__name')
    
    # Fields to be displayed in the detail view (form view)
    fields = ('farmer', 'production_type', 'session', 'date', 'output', 'remarks', 'animal')
    
    # Make 'animal' field optional
    raw_id_fields = ('animal',)
    
    # Enable ordering by date
    ordering = ('-date',)

# Register the model with the custom admin interface
admin.site.register(Production, ProductionAdmin)
@admin.register(ProductionRecord)
class ProductionRecordAdmin(admin.ModelAdmin):
    list_display = ("commodity", "quantity", "farm", "farmer", "created_at", "last_updated")
    list_filter = ("commodity", "farm", "created_at")
    search_fields = ("commodity", "farm__name", "farmer__username", "quantity")
    ordering = ("-created_at",)

