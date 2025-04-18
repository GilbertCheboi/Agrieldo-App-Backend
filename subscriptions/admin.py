from django.contrib import admin
from .models import Subscription, Package, Service

# Register the Package model
@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at', 'updated_at']

# Register the Service model
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'package']
    search_fields = ['name']
    list_filter = ['package']

# Register the Subscription model with custom admin
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_owner_username', 'package', 'number_of_cows', 'payment_status', 'created_at', 'updated_at']
    
    def get_owner_username(self, obj):
        return obj.owner.username if obj.owner else 'No Owner'
    get_owner_username.admin_order_field = 'owner'  # Allows ordering by 'owner'
    get_owner_username.short_description = 'Owner'

    search_fields = ['owner__username', 'package__name']
    list_filter = ['payment_status', 'package', 'created_at']
