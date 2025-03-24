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
        fields = ['id', 'animal', 'date', 'type', 'details', 'is_sick', 'clinical_signs', 'diagnosis', 'treatment', 'cost']  # Updated fields
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
class LactationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LactationStatus
        fields = ['lactation_number', 'days_in_milk', 'is_milking', 'last_calving_date', 'expected_calving_date']


class LifetimeStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifetimeStats
        fields = ['total_milk', 'avg_yield', 'calves']

class AnimalSerializer(serializers.ModelSerializer):
    images = AnimalImageSerializer(many=True, read_only=True)
    health_records = HealthRecordSerializer(many=True, read_only=True)
    production_data = ProductionDataSerializer(many=True, read_only=True)
    reproductive_history = ReproductiveHistorySerializer(many=True, read_only=True)
    feed_management = FeedManagementSerializer(many=True, read_only=True)
    financial_details = FinancialDetailsSerializer(read_only=True)
    lactation_status = LactationStatusSerializer(read_only=True)
    lifetime_stats = LifetimeStatsSerializer(read_only=True)
    farm = FarmSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    is_pregnant = serializers.SerializerMethodField()
    latest_milk_yield = serializers.SerializerMethodField()

    class Meta:
        model = Animal
        fields = [
            'tag','id', 'name', 'breed', 'dob', 'gender', 'farm', 'owner', 'assigned_worker',
             'images', 'health_records', 'production_data',
            'reproductive_history', 'feed_management', 'financial_details',
            'lactation_status', 'lifetime_stats', 'category', 'is_pregnant',
            'latest_milk_yield'
        ]

    def get_category(self, obj):
        return obj.category()

    def get_is_pregnant(self, obj):
        return obj.is_pregnant

    def get_latest_milk_yield(self, obj):
        latest_production = obj.production_data.order_by('-date').first()
        return latest_production.milk_yield if latest_production else 0.0
