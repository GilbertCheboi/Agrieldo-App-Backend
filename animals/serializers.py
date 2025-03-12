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
