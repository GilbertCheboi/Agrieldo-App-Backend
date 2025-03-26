from rest_framework import serializers
from .models import Feed

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['id', 'name', 'quantity_kg', 'price_per_kg', 'created_at', 'owner']
