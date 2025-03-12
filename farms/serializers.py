# farm_app/serializers.py
from rest_framework import serializers
from .models import Farm, FarmStaff, FarmVet
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model to include basic user details."""
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]

class FarmStaffSerializer(serializers.ModelSerializer):
    """Serializer for farm staff, linking to UserSerializer."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = FarmStaff
        fields = ["id", "user"]

class VetStaffSerializer(serializers.ModelSerializer):
    """Serializer for farm vets, linking to UserSerializer."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = FarmVet
        fields = ["id", "user"]

class FarmSerializer(serializers.ModelSerializer):
    """Serializer for Farm model, ensuring proper staff serialization."""
    owner = serializers.StringRelatedField(read_only=True)  # Display owner's username
    farm_staff = FarmStaffSerializer(many=True, read_only=True)  # Use related_name from model
    vet_staff = VetStaffSerializer(many=True, read_only=True)    # Use related_name from model

    class Meta:
        model = Farm
        fields = [
            "id", "name", "owner", "farm_staff", "vet_staff", "location",
            "latitude", "longitude", "type"
        ]

    def create(self, validated_data):
        """Ensure the authenticated user is set as the farm owner."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["owner"] = request.user
        return super().create(validated_data)
