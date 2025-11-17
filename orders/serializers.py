from rest_framework import serializers
from .models import UnifiedOrder, UnifiedOrderItem
from feed_store.models import FeedOrder
from drug_store.models import DrugOrder

class UnifiedOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnifiedOrderItem
        fields = "__all__"


class UnifiedOrderSerializer(serializers.ModelSerializer):
    items = UnifiedOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = UnifiedOrder
        fields = "__all__"

