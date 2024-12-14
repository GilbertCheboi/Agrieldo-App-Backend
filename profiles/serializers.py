from rest_framework import serializers
from .models import Farmer, Vet

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['user', 'phone_number', 'farm_location', 'image', 'first_name', 'second_name', 'banner']
        read_only_fields = ['user']  # Only the user cannot be modified

class VetSerializer(serializers.ModelSerializer):
    # Add relevant fields for the vet profile, assuming Vet has a related user model with latitude and longitude
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone_number = serializers.CharField()
    is_available = serializers.BooleanField()
    last_active = serializers.DateTimeField()

    class Meta:
        model = Vet
        fields = ['first_name', 'last_name', 'phone_number', 'is_available', 'last_active']
