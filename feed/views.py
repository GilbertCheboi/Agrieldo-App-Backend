from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Feed
from .serializers import FeedSerializer
from animals.models import Animal, FeedManagement
from datetime import date

import logging
logger = logging.getLogger('feed')  # Use your app name here



class FeedListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to handle top-ups without serializer validation."""
        name = request.data.get('name')
        quantity_kg = request.data.get('quantity_kg')
        price_per_kg = request.data.get('price_per_kg')

        logger.debug(f"Received data: {request.data}")

        try:
            quantity_kg = float(quantity_kg)
            price_per_kg = float(price_per_kg) if price_per_kg is not None else None
            owner = request.user

            feed = Feed.objects.filter(name=name, owner=owner).first()

            if feed:
                # Top-up: Bypass serializer, update directly
                feed.add_feed(quantity_kg, price_per_kg)
                feed_serializer = FeedSerializer(feed, context={'request': request})
                logger.debug(f"Feed topped up: {feed_serializer.data}")
                return Response(feed_serializer.data, status=status.HTTP_200_OK)
            else:
                # New feed: Use serializer for validation and creation
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                feed = serializer.save(owner=owner, quantity_kg=quantity_kg, price_per_kg=price_per_kg)
                logger.debug(f"New feed created: {feed}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.error(f"ValueError: {e}")
            return Response({"error": "Invalid quantity or price"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
