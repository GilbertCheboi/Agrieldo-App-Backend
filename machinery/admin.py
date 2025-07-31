from django.contrib import admin
from .models import Machinery, MachineryOrder, MachineryVendorApplication

@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'purchase_date', 'condition', 'owner', 'is_available')
    search_fields = ('name', 'model')
    list_filter = ('condition', 'is_available')

@admin.register(MachineryVendorApplication)
class MachineryVendorApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'phone_number', 'type_of_machine', 'model', 'price_per_day',
        'submitted_at', 'approved', 'is_active'
    )

@admin.register(MachineryOrder)
class MachineryOrderAdmin(admin.ModelAdmin):
    list_display = (
        'vendor', 'machinery', 'customer_name', 'customer_phone',
        'land_size_acres', 'start_date', 'end_date', 'created_at'
    )
