from rest_framework import serializers
from .models import Production, ProductionRecord

class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = ['farmer', 'production_type', 'date', 'output', 'session', 'animal', 'remarks']
        extra_kwargs = {
            'farmer': {'required': False},  # Make sure 'farmer' is not required here
        }

    def create(self, validated_data):
        # Automatically assign the logged-in user as the farmer
        user = self.context['request'].user  # Get the user from the request context
        validated_data['farmer'] = user
        return super().create(validated_data)


class ProductionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionRecord
        fields = ['id', 'farm', 'commodity', 'quantity', 'created_at']
        read_only_fields = ['id', 'created_at']  # Prevent modification of created_at

