from rest_framework import serializers
from .models import Production

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
