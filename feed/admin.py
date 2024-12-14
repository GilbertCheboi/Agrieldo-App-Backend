from django.contrib import admin
from .models import Feed

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'feed_type', 'date', 'starting_balance', 'amount_added', 'amount_consumed', 'closing_balance')
    list_filter = ('feed_type', 'date')
    search_fields = ('farmer__username', 'feed_type')
    date_hierarchy = 'date'
    ordering = ('-date', 'farmer')

    fieldsets = (
        (None, {
            'fields': ('farmer', 'feed_type', 'date')
        }),
        ('Feed Details', {
            'fields': ('starting_balance', 'amount_added', 'amount_consumed', 'closing_balance')
        }),
    )

    readonly_fields = ('closing_balance',)
