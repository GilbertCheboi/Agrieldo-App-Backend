from rest_framework import serializers
from .models import Farmer, Vet, Lead, Staff, MechanizationAgent, VetRequest
from farms.models import Farm
from animals.models import Animal
from accounts.models import User

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
        fields = [
            "id",
            "farmer",
            "vet",
            "signs",
            "message",
            "animal_image",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "farmer", "status", "created_at"]  # remove 'vet' from read-only

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = ['id', 'tag', 'name', 'breed', 'dob', 'gender', 'assigned_worker']

class FarmSerializer(serializers.ModelSerializer):
    animals = AnimalSerializer(many=True, read_only=True)  # nested animals

    class Meta:
        model = Farm
        fields = ['id', 'name', 'type', 'location', 'latitude', 'longitude', 'animals']

class UserDetailSerializer(serializers.ModelSerializer):
    farms = FarmSerializer(source='owned_farms', many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'farms']
