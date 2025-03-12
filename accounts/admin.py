from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Add 'phone_number', 'latitude', 'longitude' to the list display
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'is_active')  
    search_fields = ('username', 'email', 'phone_number')  # Allow searching by phone_number too
    list_filter = ('is_staff', 'is_active')  # Filter by active or staff status

    # Optimize queries by selecting related profiles
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Add related profiles if they exist, for future enhancements.
        return qs.select_related('farmer_profile', 'vet_profile')
    
    # Optionally, customize form fields and display options if needed
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Profile Information', {
            'fields': ('phone_number', 'user_type', 'fcm_token')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'phone_number')
        }),
    )

    # Optionally, add more methods if you need custom behavior for admin actions
