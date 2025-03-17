from rest_framework import serializers
from .models import Produce, Store, Outlet, Inventory, Transaction


class ProduceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produce
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

    def create(self, validated_data):
        store = validated_data.get('store')
        outlet = validated_data.get('outlet')
        produce = validated_data.get('produce')
        quantity = validated_data.get('quantity')

        # Optional: handle created_at
        created_at = validated_data.get('created_at', None)
        if not created_at:
            created_at = timezone.now()

        # If outlet is set, it's a transfer - deduct from store
        if outlet:
            # Check if store has sufficient stock
            from_store = Inventory.objects.filter(
                produce=produce,
                store=store,
                outlet__isnull=True
            ).order_by('-created_at').first()

            if not from_store or from_store.total_quantity < quantity:
                raise serializers.ValidationError("Not enough stock in store to transfer.")

            # Deduct from store
            from_store.total_quantity -= quantity
            from_store.save()

        # Now create the new inventory entry (for outlet or store addition)
        inventory = Inventory.objects.create(
            produce=produce,
            store=store,
            outlet=outlet,
            quantity=quantity,
            total_quantity=quantity,
            created_at=created_at
        )

        return inventory

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

    def validate(self, data):
        transaction_type = data.get('transaction_type')
        if transaction_type == 'ADD_TO_STORE' and not data.get('store'):
            raise serializers.ValidationError("Store is required for ADD_TO_STORE transaction.")
        if transaction_type == 'STORE_TO_OUTLET' and (not data.get('store') or not data.get('destination_outlet')):
            raise serializers.ValidationError("Store and Destination Outlet are required for STORE_TO_OUTLET transaction.")
        if transaction_type == 'OUTLET_TRANSFER' and (not data.get('source_outlet') or not data.get('destination_outlet')):
            raise serializers.ValidationError("Both source and destination outlets are required for OUTLET_TRANSFER transaction.")
        return data

