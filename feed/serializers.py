from rest_framework import serializers
from .models import Feed

class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = [
            'id', 
            'farmer', 
            'feed_type', 
            'date', 
            'starting_balance', 
            'closing_balance', 
            'amount_added', 
            'amount_consumed'
        ]
        read_only_fields = ['closing_balance', 'farmer']
