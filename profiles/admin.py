from django.contrib import admin
from django.utils import timezone  # Import timezone
from .models import Vet, Farmer

class VetAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_available', 'last_active')
    list_filter = ('is_available',)
    search_fields = ('user__username', 'phone_number')
    list_editable = ('is_available',)

    # Update last_active field on save
    def save_model(self, request, obj, form, change):
        if change:  # Only update last_active on updates, not on creation
            obj.last_active = timezone.now()
        super().save_model(request, obj, form, change)

admin.site.register(Vet, VetAdmin)

class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Farmer, FarmerAdmin)

