from rest_framework import serializers
from .models import MarketListing
from animals.models import Animal
from animals.serializers import AnimalSerializer  # you already have this

class MarketListingSerializer(serializers.ModelSerializer):
    animal = AnimalSerializer(read_only=True)

    class Meta:
        model = MarketListing
        fields = [
            'id',
            'animal',
            'seller',
            'price',
            'description',
            'image',
            'status',
            'created_at',
        ]
        read_only_fields = ['seller', 'animal', 'status']
class CreateListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketListing
        fields = ['price', 'description', 'image']

