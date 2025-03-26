from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Feed
from .serializers import FeedSerializer
from animals.models import Animal, FeedManagement
from datetime import date

class FeedListCreateView(generics.ListCreateAPIView):  # Changed to ListCreateAPIView
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class FeedAnimalsView(APIView):
    def post(self, request):
        category = request.data.get('category')
        feed_id = request.data.get('feed_id')
        quantity_per_animal = request.data.get('quantity_per_animal')

        if not all([category, feed_id, quantity_per_animal]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity_per_animal = float(quantity_per_animal)
            feed = Feed.objects.get(id=feed_id, owner=request.user)
            animals = Animal.objects.filter(category=category)
            num_animals = animals.count()

            if num_animals == 0:
                return Response({"error": "No animals in this category"}, status=status.HTTP_400_BAD_REQUEST)

            total_feed = quantity_per_animal * num_animals

            if feed.deduct_feed(total_feed):
                for animal in animals:
                    FeedManagement.objects.create(
                        animal=animal,
                        date=date.today(),
                        type=feed.name,
                        quantity=quantity_per_animal,
                        cost_per_unit=feed.price_per_kg,
                    )
                return Response({"message": "Animals fed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Not enough feed in store"}, status=status.HTTP_400_BAD_REQUEST)
        except Feed.DoesNotExist:
            return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)
