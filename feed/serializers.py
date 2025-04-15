# serializers.py
from rest_framework import serializers
from .models import Feed, FeedingPlan, FeedingPlanItem

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



class FeedingPlanItemSerializer(serializers.ModelSerializer):
    feed_name = serializers.CharField(source='feed.name', read_only=True)
    feed_id = serializers.PrimaryKeyRelatedField(source='feed', queryset=Feed.objects.all())

    class Meta:
        model = FeedingPlanItem
        fields = ['id', 'feed_id', 'feed_name', 'quantity_per_animal']

class FeedingPlanSerializer(serializers.ModelSerializer):
    items = FeedingPlanItemSerializer(many=True)

    class Meta:
        model = FeedingPlan
        fields = ['id', 'name', 'items', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        plan = FeedingPlan.objects.create(**validated_data)
        for item_data in items_data:
            FeedingPlanItem.objects.create(plan=plan, **item_data)
        return plan

    def validate(self, data):
        if not data.get('items'):
            raise serializers.ValidationError("At least one feed item is required.")
        feeds = [item['feed'] for item in data['items']]
        user = self.context['request'].user
        if any(feed.owner != user for feed in feeds):
            raise serializers.ValidationError("All feeds must belong to you.")
        return data
