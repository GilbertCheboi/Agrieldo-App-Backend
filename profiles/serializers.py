from rest_framework import serializers
from .models import Farmer, Vet, Lead, Staff, MechanizationAgent, VetRequest

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['user', 'phone_number', 'farm_location', 'image', 'first_name', 'second_name', 'banner']
        read_only_fields = ['user']  # Only the user cannot be modified

class VetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    name = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = Vet
        fields = [
            "id", "user_id", "name",
            "phone_number", "latitude", "longitude",
            "is_available", "last_active",
            "distance_km"
        ]

    def get_name(self, obj):
        # fallback: if no first/last name, use username
        first = (obj.user.first_name or "").strip()
        last  = (obj.user.last_name or "").strip()
        if first or last:
            return f"{first} {last}".strip()
        return obj.user.username

    def get_distance_km(self, obj):
        d = getattr(obj, "_distance_km", None)
        return round(d, 2) if d is not None else None


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['user', 'phone_number', 'farm_location', 'image', 'first_name', 'second_name', 'banner']
        read_only_fields = ['user']  # Only the user cannot be modified



class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

class MechanizationAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanizationAgent
        fields = '__all__'

class VetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetRequest
        fields = ["id", "farmer", "latitude", "longitude", "status", "created_at"]
        read_only_fields = ["id", "farmer", "status", "created_at"]

    # Auto-assign farmer from request.user
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["farmer"] = user
        return super().create(validated_data)