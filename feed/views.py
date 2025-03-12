from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from django.db.models import Sum
from .models import Feed, FeedTransaction
from .serializers import FeedSerializer, FeedTransactionSerializer
from datetime import timedelta
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
# Feed List & Create View
class FeedListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only logged-in users access it

    def get(self, request):
        # Return feeds only for the logged-in user
        feeds = Feed.objects.filter(owner=request.user)
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # Automatically assign owner
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Feed Retrieve, Update & Delete View
class FeedDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Feed.objects.get(pk=pk)
        except Feed.DoesNotExist:
            return None

    def get(self, request, pk):
        feed = self.get_object(pk)
        if feed is None:
            return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedSerializer(feed)
        return Response(serializer.data)

    def put(self, request, pk):
        feed = self.get_object(pk)
        if feed is None:
            return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedSerializer(feed, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        feed = self.get_object(pk)
        if feed is None:
            return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)
        feed.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Feed Transaction List & Create View
class FeedTransactionListCreateAPIView(APIView):
    def get(self, request):
        transactions = FeedTransaction.objects.all()
        serializer = FeedTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedTransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Daily Feed Consumption View
class DailyFeedConsumptionAPIView(APIView):
    def get(self, request):
        today = now().date()
        start_date = today - timedelta(days=6)  # Fetch last 7 days including today

        data = (
            FeedTransaction.objects
            .filter(timestamp__date__gte=start_date, action='CONSUME')
            .values('feed__name', 'timestamp__date')
            .annotate(total_consumed=Sum('quantity_kg'))
            .order_by('timestamp__date')
        )

        # Reformat data to group by feed type
        consumption_data = {}
        for entry in data:
            feed_name = entry['feed__name']
            date_str = entry['timestamp__date'].strftime("%Y-%m-%d")  # ✅ Convert date to string
            quantity = entry['total_consumed']

            if feed_name not in consumption_data:
                consumption_data[feed_name] = {}

            consumption_data[feed_name][date_str] = quantity

        # Format response
        formatted_response = {
            "dates": sorted(set(entry["timestamp__date"].strftime("%Y-%m-%d") for entry in data)),  # ✅ Convert dates to strings
            "consumption": consumption_data
        }

        return Response(formatted_response)
