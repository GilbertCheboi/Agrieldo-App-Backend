# admin.py
from django.contrib import admin
from .models import Subscriber, Newsletter

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'send_date', 'is_sent')
    list_filter = ('is_sent', 'send_date')
    search_fields = ('subject',)

