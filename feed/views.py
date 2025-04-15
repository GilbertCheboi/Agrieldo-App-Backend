from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Feed, FeedingPlan
from .serializers import FeedSerializer, FeedingPlanSerializer
from animals.models import Animal, FeedManagement
from datetime import date, datetime
from django.utils import timezone
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



class FeedingPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedingPlanSerializer

    def get_queryset(self):
        return FeedingPlan.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        logger.debug(f"Feeding plan created: {serializer.data}")




class FeedAnimalsView(APIView):
    def post(self, request):
        category = request.data.get('category')
        plan_id = request.data.get('plan_id')
        feeding_date = request.data.get('feeding_date')  # Get the feeding date

        # Validate required fields
        if not all([category, plan_id, feeding_date]):
            return Response(
                {"error": "Category, plan_id, and feeding_date are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate feeding_date format
        try:
            feeding_date = datetime.strptime(feeding_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid feeding_date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plan = FeedingPlan.objects.get(id=plan_id, owner=request.user)
            animals = [animal for animal in Animal.objects.filter(owner=request.user) if animal.category() == category]
            num_animals = len(animals)

            if num_animals == 0:
                return Response(
                    {"error": "No animals in this category"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check and deduct feed for each item in the plan
            for item in plan.items.all():
                total_feed = float(item.quantity_per_animal) * num_animals
                if not item.feed.deduct_feed(total_feed):
                    return Response(
                        {"error": f"Not enough {item.feed.name} in store"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Record feeding for each animal
            for animal in animals:
                for item in plan.items.all():
                    FeedManagement.objects.create(
                        animal=animal,
                        date=feeding_date,  # Use provided feeding_date
                        type=item.feed.name,
                        quantity=item.quantity_per_animal,
                        cost_per_unit=item.feed.price_per_kg or 0.0,
                    )
            logger.debug(f"Fed {num_animals} animals in {category} with plan {plan.name} on {feeding_date}")
            return Response(
                {"message": f"Fed {num_animals} animals successfully"},
                status=status.HTTP_200_OK
            )

        except FeedingPlan.DoesNotExist:
            return Response(
                {"error": "Feeding plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError:
            return Response(
                {"error": "Invalid quantity in plan"},
                status=status.HTTP_400_BAD_REQUEST
            )
