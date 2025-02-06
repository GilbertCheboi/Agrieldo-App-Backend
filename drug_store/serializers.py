from rest_framework import serializers
from .models import DrugCategory, Drug, DrugOrder

class DrugCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugCategory
        fields = ['id', 'name', 'description', 'created_at']

class DrugSerializer(serializers.ModelSerializer):
    category = DrugCategorySerializer(read_only=True)

    class Meta:
        model = Drug
        fields = ['id', 'name', 'category', 'price', 'stock_quantity', 'description', 'usage_instructions', 'created_at']

class DrugOrderSerializer(serializers.ModelSerializer):
    drug = DrugSerializer(read_only=True)

    class Meta:
        model = DrugOrder
        fields = ['id', 'customer_name', 'customer_contact', 'drug', 'quantity', 'total_price', 'order_date']
