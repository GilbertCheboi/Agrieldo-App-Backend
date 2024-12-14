from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Feed
from .serializers import FeedSerializer
from rest_framework.generics import ListAPIView


class FeedRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        user = request.user

        # Ensure a feed record exists or create a new one
        feed_record, created = Feed.objects.get_or_create(
            farmer=user,
            feed_type=data['feed_type'],
            date=data['date'],
            defaults={
                'starting_balance': data['starting_balance'],
                'amount_added': data['amount_added'],
                'amount_consumed': data['amount_consumed'],
            },
        )
        
        if not created:
            # Update existing record
            feed_record.amount_added = data['amount_added']
            feed_record.amount_consumed = data['amount_consumed']
            feed_record.save()

        serializer = FeedSerializer(feed_record)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class FarmerFeedListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.filter(farmer=self.request.user).order_by('-date')