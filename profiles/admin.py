from django.contrib import admin
from django.utils import timezone  # Import timezone
from .models import Vet, Farmer, Lead, Staff, MechanizationAgent, VetRequest

class VetAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_available', 'last_active', 'latitude', 'longitude')
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

class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

admin.site.register(Staff, StaffAdmin)

class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'status', 'source', 'created_at')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'referral_name', 'referral_phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Personal Information", {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role'),
        }),
        ("Lead Details", {
            'fields': ('source', 'referral_name', 'referral_phone_number', 'status', 'description'),
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

admin.site.register(Lead, LeadAdmin)

# -----------------------------
# Mechanization Agent Admin
# -----------------------------
class MechanizationAgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number', 'location')

admin.site.register(MechanizationAgent, MechanizationAgentAdmin)

class VetRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'vet', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('farmer__user__username', 'vet__user__username', 'message', 'signs')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Request Info", {
            'fields': ('farmer', 'vet', 'message', 'signs', 'animal_image', 'status'),
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at'),
        }),
    )

# ✅ Correct VetRequestAdmin (registered properly)
@admin.register(VetRequest)
class VetRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'vet', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('farmer__user__username', 'vet__user__username', 'message', 'signs')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Request Info", {
            'fields': ('farmer', 'vet', 'message', 'signs', 'animal_image', 'status'),
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at'),
        }),
    )