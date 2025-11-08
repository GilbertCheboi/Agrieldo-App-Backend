# serializers.py
from rest_framework import serializers
from .models import Feed, FeedingPlan, FeedingPlanItem, Store
from farms.models import Farm



class StoreSerializer(serializers.ModelSerializer):
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'farm', 'farm_name', 'owner', 'owner_name', 'created_at']
        read_only_fields = ['owner', 'created_at', 'owner_name', 'farm_name']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Store name cannot be empty.")
        return value


class FeedSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Feed
        fields = ['id', 'name', 'quantity_kg', 'price_per_kg', 'store', 'store_name', 'created_at', 'owner']
        read_only_fields = ['owner', 'created_at']

    def validate(self, attrs):
        """Ensure user can only add feed to stores of farms they belong to."""
        request = self.context['request']
        user = request.user
        store = attrs.get('store')

        if store:
            farm = store.farm
            if not (farm.owner == user or farm.farm_staff.filter(user=user).exists()):
                raise serializers.ValidationError("You are not authorized to add feed to this store.")
        else:
            raise serializers.ValidationError("Feed must be associated with a valid store.")

        return attrs

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Feed name is required.")
        return value

    def validate_quantity_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


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

    def validate(self, data):
        """Ensure all feeds belong to a farm where the user is owner or staff."""
        if not data.get('items'):
            raise serializers.ValidationError("At least one feed item is required.")

        request = self.context['request']
        user = request.user
        feeds = [item['feed'] for item in data['items']]

        for feed in feeds:
            if not (feed.owner == user or feed.store.farm.farm_staff.filter(user=user).exists()):
                raise serializers.ValidationError(
                    f"You are not authorized to use feed '{feed.name}' — it doesn't belong to your farm."
                )
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['owner'] = self.context['request'].user
        plan = FeedingPlan.objects.create(**validated_data)
        for item_data in items_data:
            FeedingPlanItem.objects.create(plan=plan, **item_data)
        return plan

