# feed/admin.py
from django.contrib import admin
from .models import Feed, FeedingPlan, FeedingPlanItem, Store



@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'owner', 'created_at')
    list_filter = ('farm', 'owner', 'created_at')
    search_fields = ('name', 'farm__name', 'owner__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Store Information', {
            'fields': ('name', 'description')
        }),
        ('Associations', {
            'fields': ('farm', 'owner')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        """Optimize query performance"""
        qs = super().get_queryset(request)
        return qs.select_related('farm', 'owner')



@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity_kg', 'price_per_kg', 'owner', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)
    list_per_page = 20

class FeedingPlanItemInline(admin.TabularInline):
    model = FeedingPlanItem
    extra = 1  # Number of empty rows to display
    fields = ('feed', 'quantity_per_animal')
    autocomplete_fields = ('feed',)

@admin.register(FeedingPlan)
class FeedingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at', 'item_count')
    list_filter = ('owner', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-created_at',)
    list_per_page = 20
    inlines = [FeedingPlanItemInline]  # Corrected: Use the class, not a string

    def item_count(self, obj):
        """Display the number of feed items in the plan."""
        return obj.items.count()
    item_count.short_description = 'Items'

@admin.register(FeedingPlanItem)
class FeedingPlanItemAdmin(admin.ModelAdmin):
    list_display = ('plan', 'feed', 'quantity_per_animal')
    list_filter = ('plan__owner', 'feed')
    search_fields = ('plan__name', 'feed__name')
    ordering = ('plan',)
    list_per_page = 20
