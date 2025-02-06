from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location', 'created_at')  # Fields to display in the admin list view
    list_filter = ('start_date', 'end_date', 'location')  # Add filtering options in the admin sidebar
    search_fields = ('title', 'location')  # Add a search bar to search by title or location
    ordering = ('-start_date',)  # Order the events by start_date in descending order

