from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import logging

from .models import Feed, FeedingPlan, Store
from .serializers import FeedSerializer, FeedingPlanSerializer, StoreSerializer
from animals.models import Animal, FeedManagement
from farms.models import Farm, FarmStaff


logger = logging.getLogger('feed')


class StoreListCreateView(generics.ListCreateAPIView):
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 1️⃣ Farms owned by this user
        owned_farms = Farm.objects.filter(owner=user)

        # 2️⃣ Farms where the user is a staff member
        staff_farms = Farm.objects.filter(farm_staff__user=user)

        # 3️⃣ Combine stores from owned & staff farms + any directly owned store
        return Store.objects.filter(
            Q(farm__in=owned_farms) |
            Q(farm__in=staff_farms) |
            Q(owner=user)
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user

        # Find a farm this user is associated with (as owner or staff)
        farm = None
        owned_farm = Farm.objects.filter(owner=user).first()
        staff_farm = Farm.objects.filter(farm_staff__user=user).first()

        if owned_farm:
            farm = owned_farm
        elif staff_farm:
            farm = staff_farm
        else:
            raise ValidationError("You must be associated with a farm to create a store.")

        # Save store with linked farm and owner
        serializer.save(owner=user, farm=farm)


class IsFarmOwnerOrStaff(permissions.BasePermission):
    """Permission to allow only farm owners or staff to perform actions."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Handle feeds (which belong to stores → farms)
        if isinstance(obj, Feed):
            farm = obj.store.farm if obj.store else None
        elif isinstance(obj, Store):
            farm = obj.farm
        elif isinstance(obj, FeedingPlan):
            farm = getattr(obj, "farm", None)
        else:
            farm = None

        if farm:
            return farm.owner == user or farm.farm_staff.filter(user=user).exists()
        return False


# ----------------------------------------
# FEED LIST & CREATE
# ----------------------------------------
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.utils.timezone import now
from .models import Feed, Store
from .serializers import FeedSerializer
import logging

logger = logging.getLogger(__name__)

class FeedListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        ✅ Allow both farm owners and staff (authenticated via token) 
        to view feeds belonging to farms they are authorized to access.
        """
        user = self.request.user
        queryset = Feed.objects.filter(
            Q(store__farm__owner=user) |
            Q(store__farm__farm_staff__user=user)
        ).distinct()

        store_id = self.request.query_params.get('store')
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        logger.debug(f"✅ Feeds queryset for {user.username}: {queryset.count()} items")
        return queryset

    def create(self, request, *args, **kwargs):
        """
        ✅ Allow authorized users (farm owner or staff) to add or top-up feed
        in a store belonging to their farm.
        """
        name = request.data.get('name')
        quantity_kg = request.data.get('quantity_kg')
        price_per_kg = request.data.get('price_per_kg')
        store_id = request.data.get('store')

        logger.debug(f"📩 Incoming feed data from {request.user}: {request.data}")

        if not store_id:
            return Response({"error": "Store ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        farm = store.farm

        # ✅ Authorization: ensure the token belongs to an allowed user
        if not (farm.owner == user or farm.farm_staff.filter(user=user).exists()):
            logger.warning(f"🚫 Unauthorized attempt by {user.username} to add feed in farm {farm.id}")
            return Response(
                {"error": "You are not authorized to add feed to this farm"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            quantity_kg = float(quantity_kg)
            price_per_kg = float(price_per_kg) if price_per_kg else None

            # ✅ Check for existing feed in same store by same user
            existing_feed = Feed.objects.filter(name=name, store=store, owner=user).first()

            if existing_feed:
                # 🔼 Top-up existing feed record
                existing_feed.add_feed(quantity_kg, price_per_kg)
                serializer = FeedSerializer(existing_feed, context={'request': request})
                logger.debug(f"🟢 Feed topped up: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # 🆕 Create new feed record
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(owner=user)
                logger.debug(f"✅ New feed created: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError:
            logger.error("❌ Invalid quantity or price input")
            return Response({"error": "Invalid quantity or price"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"⚠️ Unexpected error during feed creation: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ----------------------------------------
# FEEDING PLAN LIST & CREATE
# ----------------------------------------
class FeedingPlanListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedingPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Allow viewing all plans owned or accessible via farm staff."""
        user = self.request.user
        return FeedingPlan.objects.filter(
            Q(owner=user) |
            Q(owner__owned_farms__farm_staff__user=user)
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)
        logger.debug(f"Feeding plan created by {user.username}")


# ----------------------------------------
# FEED ANIMALS
# ----------------------------------------

class FeedAnimalsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        category = request.data.get('category')
        plan_id = request.data.get('plan_id')
        feeding_date = request.data.get('feeding_date')
        store_id = request.data.get('store_id')  # <- this comes from the client

        if not all([category, plan_id, feeding_date, store_id]):
            return Response(
                {"error": "category, plan_id, feeding_date, and store_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate feeding_date
        try:
            feeding_date = datetime.strptime(feeding_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid feeding_date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            plan = FeedingPlan.objects.get(id=plan_id)
            user = request.user

            # Check plan ownership
            if not (plan.owner == user or plan.owner.owned_farms.filter(farm_staff__user=user).exists()):
                return Response(
                    {"error": "You are not authorized to use this feeding plan"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Map store_id to Farm object
            try:
                farm = Farm.objects.get(id=store_id)
            except Farm.DoesNotExist:
                return Response(
                    {"error": f"Farm with id {store_id} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Filter animals by farm and category
            animals = [
                animal for animal in Animal.objects.filter(owner=plan.owner, farm=farm)
                if animal.category().strip().lower() == category.strip().lower()
            ]
            num_animals = len(animals)

            if num_animals == 0:
                return Response(
                    {"error": f"No animals found in category '{category}' for farm {farm.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Deduct feed
            for item in plan.items.all():
                total_feed = float(item.quantity_per_animal) * num_animals
                if not item.feed.deduct_feed(total_feed):
                    return Response(
                        {"error": f"Not enough {item.feed.name} in store"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Record feeding
            for animal in animals:
                for item in plan.items.all():
                    FeedManagement.objects.create(
                        animal=animal,
                        date=feeding_date,
                        type=item.feed.name,
                        quantity=item.quantity_per_animal,
                        cost_per_unit=item.feed.price_per_kg or 0.0,
                    )

            return Response(
                {"message": f"Fed {num_animals} animals successfully"},
                status=status.HTTP_200_OK
            )

        except FeedingPlan.DoesNotExist:
            return Response(
                {"error": "Feeding plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )

