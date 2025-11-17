# farm_app/serializers.py
from rest_framework import serializers
from .models import Farm, FarmStaff, FarmVet
from django.contrib.auth import get_user_model

# 🧩 Import your Store model + serializer from the feed app
from feed.models import Store
from feed.serializers import StoreSerializer

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
    """Serializer for Farm model, ensuring proper staff and store serialization."""
    owner = serializers.StringRelatedField(read_only=True)  # Displays owner's username
    farm_staff = FarmStaffSerializer(many=True, read_only=True)
    vet_staff = VetStaffSerializer(many=True, read_only=True)

    # ✅ NEW: Include feed stores related to this farm
    feed_stores = StoreSerializer(many=True, read_only=True)

    # Image handling (writable, optional)
    image = serializers.ImageField(required=False, allow_null=True, use_url=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "name",
            "owner",
            "farm_staff",
            "vet_staff",
            "feed_stores",  # ✅ include this
            "location",
            "latitude",
            "longitude",
            "type",
            "image",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Ensure the authenticated user is set as the farm owner."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["owner"] = request.user
        return super().create(validated_data)

