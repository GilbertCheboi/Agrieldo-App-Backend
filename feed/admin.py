from django.contrib import admin
from .models import Feed, FeedTransaction
from django.utils.html import format_html


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_kg', 'created_at', 'owner', 'image_preview')  # Added 'owner'
    search_fields = ('name', 'owner__username')  # Allow searching by owner's username
    list_filter = ('created_at', 'owner')  # Optional: filter by owner
    fields = ('name', 'quantity_kg', 'created_at', 'owner', 'image')  # Show owner in form

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

@admin.register(FeedTransaction)
class FeedTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'feed', 'quantity_kg', 'action', 'timestamp')
    search_fields = ('user__username', 'feed__name')
    list_filter = ('action', 'timestamp')
    autocomplete_fields = ('user', 'feed')
