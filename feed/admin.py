from django.contrib import admin
from .models import Feed

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_kg', 'price_per_kg', 'owner', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('name',)
