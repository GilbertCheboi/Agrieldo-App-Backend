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

