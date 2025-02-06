from rest_framework import serializers
from .models import Category, FeedProduct, Order

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class FeedProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = FeedProduct
        fields = ['id', 'name', 'category', 'price', 'quantity_in_stock', 'description', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    product = FeedProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'customer_contact', 'product', 'quantity', 'total_price', 'order_date']
