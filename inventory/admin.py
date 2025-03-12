from django.contrib import admin
from .models import Produce, Store, Outlet, Inventory, Transaction


@admin.register(Produce)
class ProduceAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_quantity', 'unit']
    search_fields = ['name']


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    search_fields = ['name']
    list_filter = ['user']


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']
    search_fields = ['name']
    list_filter = ['user']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['produce', 'store', 'outlet', 'quantity', 'user', 'last_updated']
    list_filter = ['store', 'outlet', 'user']
    search_fields = ['produce__name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'produce', 'quantity', 'store', 'source_outlet', 'destination_outlet', 'user', 'timestamp']
    list_filter = ['transaction_type', 'store', 'source_outlet', 'destination_outlet', 'user']
    search_fields = ['produce__name']
    readonly_fields = ['timestamp']

