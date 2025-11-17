from django.contrib import admin
from .models import Category, FeedProduct, FeedOrder


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(FeedProduct)
class FeedProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'quantity_in_stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(FeedOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'product', 'quantity', 'total_price', 'order_date')
    list_filter = ('order_date',)
    search_fields = ('customer_name', 'product__name')

