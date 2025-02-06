from rest_framework import serializers
from .models import VetRequest

class VetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetRequest
        fields = ['id', 'farmer', 'description', 'service_type', 'status', 'image']  # Excluding 'location' for now

    # Optionally, you can add custom validation if needed
    def validate_description(self, value):
        if not value:
            raise serializers.ValidationError("Description is required.")
        return value

    def validate_service_type(self, value):
        if not value:
            raise serializers.ValidationError("Service type is required.")
        return value

