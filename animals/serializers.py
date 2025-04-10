# animals/serializers.py
from rest_framework import serializers
from .models import (
    Animal, AnimalImage, HealthRecord, ProductionData, ReproductiveHistory,
    FeedManagement, FinancialDetails, LactationPeriod, LifetimeStats
)
from farms.models import Farm

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = [ 'name', 'location']

class AnimalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalImage
        fields = ['image']


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = ['id', 'animal', 'date', 'type', 'details', 'is_sick', 'clinical_signs', 'diagnosis', 'treatment', 'cost']  # Updated fields
        read_only_fields = ['id']  # ID remains read-only

    def validate_animal(self, value):
        if not value:
            raise serializers.ValidationError("Animal is required.")
        return value

class ProductionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionData
        fields = ['animal', 'id', 'date', 'session', 'milk_yield', 'milk_price_per_liter', 'feed_consumption', 'scc', 'fat_percentage', 'protein_percentage']
        read_only_fields = ['id']  # ID is auto-generated, should not be writable

    def validate(self, data):
        # Optional: Add custom validation if needed
        return data


class DailyProductionSummarySerializer(serializers.Serializer):
    date = serializers.DateField()
    total_milk_yield = serializers.FloatField()
    avg_price_per_liter = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_feed_consumption = serializers.FloatField()
    avg_scc = serializers.FloatField()
    avg_fat_percentage = serializers.FloatField()
    avg_protein_percentage = serializers.FloatField()


class ReproductiveHistorySerializer(serializers.ModelSerializer):
    expected_calving_date = serializers.DateField(read_only=True)

    class Meta:
        model = ReproductiveHistory
        fields = ['id', 'animal', 'date', 'event', 'details', 'expected_calving_date', 'cost']  # Added 'id' and 'animal'

class FeedManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedManagement
        fields = ['id', 'date', 'type', 'quantity', 'cost_per_unit', 'total_cost']
        read_only_fields = ['id', 'total_cost']  # 'total_cost' is calculated in the model

    def validate(self, data):
        # Ensure quantity and cost_per_unit are non-negative
        if data.get('quantity', 0) < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        if data.get('cost_per_unit', 0) < 0:
            raise serializers.ValidationError("Cost per unit cannot be negative.")
        return data


class FinancialDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialDetails
        fields = ['total_feed_cost', 'total_vet_cost', 'total_breeding_cost', 'total_revenue_from_milk', 'total_cost']

class LactationPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = LactationPeriod
        fields = ['id', 'lactation_number', 'days_in_milk', 'is_milking', 'last_calving_date', 'expected_calving_date', 'end_date']

class LifetimeStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifetimeStats
        fields = ['total_milk', 'avg_yield', 'calves']


class AnimalSerializer(serializers.ModelSerializer):
    # Allow images to be writable
    images = AnimalImageSerializer(many=True, required=False)

    health_records = HealthRecordSerializer(many=True, read_only=True)
    production_data = ProductionDataSerializer(many=True, read_only=True)
    reproductive_history = ReproductiveHistorySerializer(many=True, read_only=True)
    feed_management = FeedManagementSerializer(many=True, read_only=True)
    financial_details = FinancialDetailsSerializer(read_only=True)
    lactation_periods = LactationPeriodSerializer(many=True, read_only=True)
    lifetime_stats = LifetimeStatsSerializer(read_only=True)
    # farm = FarmSerializer(read_only=True)
    farm = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all())
    category = serializers.SerializerMethodField()
    is_pregnant = serializers.SerializerMethodField()
    latest_milk_yield = serializers.SerializerMethodField()
    class Meta:
        model = Animal
        fields = [
            'tag','id', 'name', 'breed', 'dob', 'gender', 'farm', 'owner',
             'images', 'health_records', 'production_data',
            'reproductive_history', 'feed_management', 'financial_details',
            'lactation_periods', 'lifetime_stats', 'category', 'is_pregnant',
            'latest_milk_yield'
        ]

    def get_category(self, obj):
        return obj.category()

    def get_is_pregnant(self, obj):
        return obj.is_pregnant

    def get_latest_milk_yield(self, obj):
        latest_production = obj.production_data.order_by('-date').first()
        return latest_production.milk_yield if latest_production else 0.0

    def create(self, validated_data):
            # Remove images data from the validated_data
            images_data = validated_data.pop('images', [])
            # Create the animal instance first
            animal = Animal.objects.create(**validated_data)
            # Now create the related AnimalImage instances if any image data is provided.
            for image_data in images_data:
                AnimalImage.objects.create(animal=animal, **image_data)
            return animal