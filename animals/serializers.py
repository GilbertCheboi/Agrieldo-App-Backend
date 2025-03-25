from django.core.files.base import ContentFile
import requests
import base64
from io import BytesIO

# animals/serializers.py
from rest_framework import serializers
from .models import (
    Animal, AnimalImage, HealthRecord, ProductionData, ReproductiveHistory,
    FeedManagement, FinancialDetails, LactationStatus, LifetimeStats
)
from farms.models import Farm

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = [ 'name', 'location']

class AnimalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalImage
        fields = ['image', 'caption']


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ['id', 'animal', 'date', 'type', 'details', 'is_sick', 'clinical_signs', 'diagnosis', 'treatment']  # Updated fields
        read_only_fields = ['id']  # ID remains read-only

    def validate_animal(self, value):
        if not value:
            raise serializers.ValidationError("Animal is required.")
        return value

class ProductionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionData
        fields = ['animal', 'id', 'date', 'session', 'milk_yield', 'feed_consumption', 'scc', 'fat_percentage', 'protein_percentage']

class ReproductiveHistorySerializer(serializers.ModelSerializer):
    expected_calving_date = serializers.DateField(read_only=True)

    class Meta:
        model = ReproductiveHistory
        fields = ['id', 'animal', 'date', 'event', 'details', 'expected_calving_date']  # Added 'id' and 'animal'
class FeedManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedManagement
        fields = ['date', 'type', 'quantity']

class FinancialDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialDetails
        fields = ['feed_cost_per_month', 'vet_expenses', 'breeding_costs', 'revenue_from_milk']

class LactationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LactationStatus
        fields = ['lactation_number', 'days_in_milk', 'is_milking', 'last_calving_date', 'expected_calving_date']


class LifetimeStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifetimeStats
        fields = ['total_milk', 'avg_yield', 'calves']

class AnimalSerializer(serializers.ModelSerializer):
    images = AnimalImageSerializer(many=True, read_only=True)  # Read images properly
    image = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    caption = serializers.CharField(write_only=True, required=False)  # Single caption for all images

    class Meta:
        model = Animal
        fields = [
            'tag', 'id', 'name', 'breed', 'dob', 'gender', 'farm', 'owner',
            'assigned_worker', 'image', 'caption', 'images'
        ]
        read_only_fields = ['owner']

    def create(self, validated_data):
        images = validated_data.pop("image", [])
        caption = validated_data.pop("caption", "")  # Only one caption for all images

        print(f"📸 Received Images: {images}, Caption: {caption}")  # Debugging

        animal = Animal.objects.create(**validated_data)

        # Create AnimalImage for each image with the same caption
        for image in images:
            AnimalImage.objects.create(animal=animal, image=image, caption=caption)

        return animal
