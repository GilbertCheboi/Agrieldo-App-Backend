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

        # ✅ Authorization check
        if not (farm.owner == user or farm.farm_staff.filter(user=user).exists()):
            logger.warning(f"🚫 Unauthorized attempt by {user.username} to add feed in farm {farm.id}")
            return Response(
                {"error": "You are not authorized to add feed to this farm"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            quantity_kg = float(quantity_kg)
            price_per_kg = float(price_per_kg) if price_per_kg else None

            # ✅ Check for existing feed by name and store (shared access)
            existing_feed = Feed.objects.filter(name=name, store=store).first()

            if existing_feed:
                # 🔼 Top-up existing shared feed
                existing_feed.add_feed(quantity_kg, price_per_kg, user=user)
                serializer = FeedSerializer(existing_feed, context={'request': request})
                logger.info(f"🟢 Feed topped up by {user.username}: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # 🆕 Create new feed record
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(owner=user, last_topped_up_by=user)
                logger.info(f"✅ New feed created by {user.username}: {serializer.data}")
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
        """
        ✅ Return all feeding plans in stores where the user is either
        the farm owner or part of the farm's staff.
        """
        user = self.request.user

        queryset = FeedingPlan.objects.filter(
            Q(store__farm__owner=user) |
            Q(store__farm__farm_staff__user=user)
        ).distinct()

        store_id = self.request.query_params.get("store")
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        logger.debug(f"✅ Feeding plans for {user.username}: {queryset.count()} items")
        return queryset

    def perform_create(self, serializer):
        """
        ✅ Allow both farm owners and staff to create feeding plans
        in stores they have access to.
        """
        user = self.request.user
        store_id = self.request.data.get("store")

        if not store_id:
            logger.warning(f"🚫 Missing store ID from {user.username}")
            raise ValueError("Store ID is required when creating a feeding plan.")

        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            logger.warning(f"🚫 Invalid store id {store_id} by {user.username}")
            raise ValueError("Store not found.")

        farm = store.farm

        # ✅ Authorization: must be farm owner or staff
        if not (farm.owner == user or farm.farm_staff.filter(user=user).exists()):
            logger.warning(f"🚫 Unauthorized feeding plan create attempt by {user.username} on store {store.id}")
            raise PermissionError("You are not authorized to create a plan for this store.")

        # ✅ Validate feeds all belong to this store
        feed_ids = [
            item.get("feed")
            for item in self.request.data.get("items", [])
            if item.get("feed")
        ]
        invalid_feeds = Feed.objects.exclude(store=store).filter(id__in=feed_ids)
        if invalid_feeds.exists():
            invalid_names = [f.name for f in invalid_feeds]
            raise ValueError(
                f"The following feeds do not belong to this store: {', '.join(invalid_names)}"
            )

        # ✅ Save feeding plan linked to this store
        serializer.save(owner=user, store=store, last_updated_by=user)
        logger.info(f"🟢 Feeding plan '{serializer.validated_data.get('name')}' created in store '{store.name}' by {user.username}")


# ----------------------------------------
# FEED ANIMALS
# ----------------------------------------

from django.db import transaction

class FeedAnimalsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        category = request.data.get('category')
        plan_id = request.data.get('plan_id')
        feeding_date = request.data.get('feeding_date')
        store_id = request.data.get('store_id')

        if not all([category, plan_id, feeding_date, store_id]):
            return Response(
                {"error": "category, plan_id, feeding_date, and store_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🗓 Validate feeding_date
        try:
            feeding_date = datetime.strptime(feeding_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid feeding_date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            store = Store.objects.select_related("farm").get(id=store_id)
        except Store.DoesNotExist:
            return Response(
                {"error": f"Store with id {store_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        farm = store.farm

        try:
            plan = FeedingPlan.objects.prefetch_related("items__feed").get(id=plan_id)
        except FeedingPlan.DoesNotExist:
            return Response(
                {"error": "Feeding plan not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        # 🛡 Check authorization
        if not (farm.owner == user or farm.farm_staff.filter(user=user).exists()):
            return Response(
                {"error": "You are not authorized to feed animals on this farm"},
                status=status.HTTP_403_FORBIDDEN
            )

        # 🐄 Get animals for the selected category
        animals = [
            animal for animal in Animal.objects.filter(farm=farm)
            if animal.category().strip().lower() == category.strip().lower()
        ]
        num_animals = len(animals)
        if num_animals == 0:
            return Response(
                {"error": f"No animals found in category '{category}' for farm {farm.name}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Deduct feeds safely
        try:
            with transaction.atomic():
                for item in plan.items.select_related("feed"):
                    total_feed = float(item.quantity_per_animal) * num_animals
                    if not item.feed.deduct_feed(total_feed):
                        raise ValueError(f"Not enough {item.feed.name} in store")

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
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": f"Fed {num_animals} animals successfully", "num_animals": num_animals},
            status=status.HTTP_200_OK
        )





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum
from datetime import date


class FeedActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, feed_id):
        """
        Returns summary and daily logs for a specific feed:
        - Added (based on quantity_kg at creation)
        - Consumed (from FeedManagement)
        - Remaining (current quantity_kg)
        """
        try:
            feed = Feed.objects.select_related("store__farm").get(id=feed_id)
        except Feed.DoesNotExist:
            return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        farm = feed.store.farm

        # Check authorization (farm owner or staff)
        if not (farm.owner == user or farm.farm_staff.filter(user=user).exists()):
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # 🧮 Get all consumption records for this feed
        consumed_logs = (
            FeedManagement.objects.filter(type=feed.name)
            .values("date")
            .annotate(consumed=Sum("quantity"))
            .order_by("-date")
        )

        # 🧮 Added and Remaining
        added_total = float(feed.quantity_kg) + float(
            sum(log["consumed"] or 0 for log in consumed_logs)
        )
        consumed_total = float(sum(log["consumed"] or 0 for log in consumed_logs))
        remaining_total = float(feed.quantity_kg)

        # 🧾 Prepare logs list
        logs = []
        for log in consumed_logs:
            logs.append(
                {
                    "date": str(log["date"]),
                    "added": 0,  # no addition log
                    "consumed": float(log["consumed"] or 0),
                }
            )

        # Add a creation entry as “added”
        logs.append(
            {
                "date": str(feed.created_at.date()),
                "added": added_total,
                "consumed": 0,
            }
        )

        # Sort descending by date
        logs = sorted(logs, key=lambda x: x["date"], reverse=True)

        return Response(
            {
                "feed": {
                    "id": feed.id,
                    "name": feed.name,
                    "store": feed.store.name,
                    "farm": farm.name,
                },
                "summary": {
                    "added": added_total,
                    "consumed": consumed_total,
                    "remaining": remaining_total,
                },
                "logs": logs,
            },
            status=status.HTTP_200_OK,
        )

