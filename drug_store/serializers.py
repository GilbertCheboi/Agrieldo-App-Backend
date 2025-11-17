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
        fields = [
            'id', 'name', 'category', 'price', 'stock_quantity',
            'description', 'usage_instructions', 'image', 'created_at'
        ]



from rest_framework.exceptions import ValidationError

class DrugOrderSerializer(serializers.ModelSerializer):
    drug = serializers.PrimaryKeyRelatedField(queryset=Drug.objects.all())

    class Meta:
        model = DrugOrder
        fields = [
            'id',
            'customer_name',
            'customer_contact',
            'drug',
            'quantity',
            'total_price',
            'order_date'
        ]
        read_only_fields = ['total_price', 'order_date']

    def create(self, validated_data):
        drug = validated_data['drug']
        quantity = validated_data['quantity']

        # 1️⃣ Check stock
        if drug.stock_quantity < quantity:
            raise ValidationError({
                "quantity": [
                    f"Only {drug.stock_quantity} units available in stock."
                ]
            })

        # 2️⃣ Calculate price
        validated_data['total_price'] = drug.price * quantity

        # 3️⃣ Reduce stock
        drug.stock_quantity -= quantity
        drug.save()

        # 4️⃣ Save order
        return super().create(validated_data)

