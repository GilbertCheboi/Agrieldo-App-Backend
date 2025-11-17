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
    feed_name = serializers.CharField(source="feed.name", read_only=True)

    class Meta:
        model = FeedingPlanItem
        fields = ['id', 'feed', "feed_name",  'quantity_per_animal']


class FeedingPlanSerializer(serializers.ModelSerializer):
    items = FeedingPlanItemSerializer(many=True)

    class Meta:
        model = FeedingPlan
        fields = [
            'id',
            'name',
            'store',
            'items',
            'owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def validate(self, data):
        """
        ✅ Ensure all feeds belong to the same store as the feeding plan
        and the user (owner or staff) is authorized to use that store.
        """
        request = self.context['request']
        user = request.user
        store = data.get('store')

        if not store:
            raise serializers.ValidationError("Store is required for a feeding plan.")

        # ✅ Authorization: user must be farm owner or staff for this store's farm
        if not (store.farm.owner == user or store.farm.farm_staff.filter(user=user).exists()):
            raise serializers.ValidationError(
                "You are not authorized to create or modify plans in this store."
            )

        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("At least one feed item is required.")

        # ✅ Ensure all selected feeds belong to the same store
        for item in items:
            feed = item['feed']
            if feed.store != store:
                raise serializers.ValidationError(
                    f"Feed '{feed.name}' does not belong to the selected store '{store.name}'."
                )

        return data

    def create(self, validated_data):
        """
        ✅ Create a feeding plan and its related items in one transaction.
        """
        items_data = validated_data.pop('items', [])
        validated_data['owner'] = self.context['request'].user

        plan = FeedingPlan.objects.create(**validated_data)

        for item_data in items_data:
            FeedingPlanItem.objects.create(plan=plan, **item_data)

        return plan

