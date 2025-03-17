# sheep_app/serializers.py
from rest_framework import serializers
from .models import Sheep, SheepHealthRecord, SheepReproduction, SheepProduction, SheepImage, SheepType
from farms.models import Farm
class SheepTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheepType
        fields = ['id', 'name', 'description', 'avg_wool_yield', 'avg_weight']

class SheepHealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheepHealthRecord
        fields = ['id', 'date', 'is_sick', 'diagnosis', 'treatment']

class SheepReproductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheepReproduction
        fields = ['id', 'mating_date', 'partner_tag', 'birth_date', 'offspring_count']

class SheepProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheepProduction
        fields = ['id', 'date', 'wool_yield', 'weight', 'shearing_date']

class SheepImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SheepImage
        fields = ['id', 'image', 'upload_date', 'description']
class SheepSerializer(serializers.ModelSerializer):
    sheep_type = SheepTypeSerializer(read_only=True)  # For reading
    sheep_type_id = serializers.PrimaryKeyRelatedField(
        queryset=SheepType.objects.all(),
        source='sheep_type',  # Maps to the sheep_type field in the model
        allow_null=True,
        write_only=True  # Only for writing
    )
    health_records = SheepHealthRecordSerializer(many=True, read_only=True)
    reproduction_records = SheepReproductionSerializer(many=True, read_only=True)
    production_records = SheepProductionSerializer(many=True, read_only=True)
    images = SheepImageSerializer(many=True, read_only=True)
    farm = serializers.PrimaryKeyRelatedField(queryset=Farm.objects.all())

    class Meta:
        model = Sheep
        fields = [
            'id', 'farm', 'tag_number', 'dob', 'sheep_type', 'sheep_type_id',
            'health_records', 'reproduction_records', 'production_records', 'images'
        ]
        read_only_fields = ['health_records', 'reproduction_records', 'production_records', 'images']
