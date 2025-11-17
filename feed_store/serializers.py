from rest_framework import serializers
from .models import Category, FeedProduct, FeedOrder


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class FeedProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = FeedProduct
        fields = [
            'id', 'name', 'category', 'price', 'quantity_in_stock',
            'description', 'image', 'created_at'
        ]

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url)
        return None


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedOrder
        fields = [
            'id', 'customer_name', 'customer_contact',
            'product', 'quantity', 'total_price', 'order_date'
        ]
        read_only_fields = ['total_price']  # calculated automatically

    def create(self, validated_data):
        product = validated_data['product']
        quantity = validated_data['quantity']

        # Auto calculate total price
        validated_data['total_price'] = product.price * quantity

        # Reduce stock
        product.quantity_in_stock -= quantity
        product.save()

        return super().create(validated_data)

