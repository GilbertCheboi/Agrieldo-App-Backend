from rest_framework import serializers
from .models import Feed, FeedTransaction

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = ['id', 'owner',  'name', 'quantity_kg', 'image']


class FeedTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedTransaction
        fields = '__all__'
class DailyConsumptionSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_consumed = serializers.FloatField()
    breakdown = serializers.ListField(child=serializers.DictField())
