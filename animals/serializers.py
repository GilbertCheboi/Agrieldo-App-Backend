# serializers.py

from rest_framework import serializers
from .models import Animal, Dairy_Cow, Beef_Cow, Sheep, Goat, DairyMedicalRecord, BeefMedicalRecord, SheepMedicalRecord, GoatMedicalRecord, AnimalGallery

class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Animal
        fields = '__all__'

class DairyCowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dairy_Cow
        fields = '__all__'
        read_only_fields = ['owner']

class BeefCowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beef_Cow
        fields = '__all__'
        read_only_fields = ['owner']


class SheepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sheep
        fields = '__all__'
        read_only_fields = ['owner']

class GoatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goat
        fields = '__all__'
        read_only_fields = ['owner']

class DairyMedicalRecordSerializer(serializers.ModelSerializer):
    veterinarian = serializers.StringRelatedField()

    class Meta:
        model = DairyMedicalRecord
        fields = '__all__'

class BeefMedicalRecordSerializer(serializers.ModelSerializer):
    veterinarian = serializers.StringRelatedField()

    class Meta:
        model = BeefMedicalRecord
        fields = '__all__'

class SheepMedicalRecordSerializer(serializers.ModelSerializer):
    veterinarian = serializers.StringRelatedField()

    class Meta:
        model = SheepMedicalRecord
        fields = '__all__'

class GoatMedicalRecordSerializer(serializers.ModelSerializer):
    veterinarian = serializers.StringRelatedField()

    class Meta:
        model = GoatMedicalRecord
        fields = '__all__'

class AnimalGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalGallery
        fields = ['id', 'animal', 'image', 'description', 'created_at']
