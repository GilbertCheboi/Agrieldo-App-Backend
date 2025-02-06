from rest_framework import serializers
from .models import Auction
from animals.models import Animal
from animals.serializers import AnimalSerializer  # Import the AnimalSerializer


class AuctionSerializer(serializers.ModelSerializer):
    animal = AnimalSerializer()  # Use AnimalSerializer to fetch animal details

    class Meta:
        model = Auction
        fields = ['id', 'animal', 'price', 'description', 'auction_end_date', 'location']

