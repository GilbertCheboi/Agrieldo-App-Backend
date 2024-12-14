from rest_framework import serializers
from .models import VetRequest

class VetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetRequest
        fields = '__all__'  # Include all fields or specify a list of fields

