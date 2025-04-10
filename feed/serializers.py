# serializers.py
from rest_framework import serializers
from .models import Feed

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['id', 'name', 'quantity_kg', 'price_per_kg', 'created_at', 'owner']
        read_only_fields = ['owner', 'created_at']

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Feed name is required.")
        if self.instance is None:  # Only check uniqueness for new feeds
            owner = self.context['request'].user
            if Feed.objects.filter(name=value, owner=owner).exists():
                raise serializers.ValidationError("A feed with this name already exists for your account.")
        return value

    def validate_quantity_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value
