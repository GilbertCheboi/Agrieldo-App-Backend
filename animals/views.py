from rest_framework import serializers  
from rest_framework.generics import ListCreateAPIView
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from django.db.models import Sum
from .models import Animal, HealthRecord, ProductionData, ReproductiveHistory
from accounts.models import User
from .serializers import AnimalSerializer, HealthRecordSerializer, ProductionDataSerializer, ReproductiveHistorySerializer
from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ( AnimalImage)
import logging

logger = logging.getLogger(__name__)

from farms.models import Farm
class AnimalListCreateView(ListCreateAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # ✅ Ensure proper parsing of images

    def get_queryset(self):
        """Return only animals belonging to the authenticated user."""
        farm_id = self.request.query_params.get("farm_id", None)
        queryset = Animal.objects.filter(owner=self.request.user)
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        return queryset

    def perform_create(self, serializer):
        """Assign the authenticated user as the owner before saving."""
        farm_id = self.request.data.get("farm")

        # ✅ Validate farm ownership
        if not farm_id or not Farm.objects.filter(id=farm_id, owner=self.request.user).exists():
            raise serializers.ValidationError({"farm": "Invalid or unauthorized farm ID."})

        # ✅ Save animal with owner
        animal = serializer.save(owner=self.request.user)

        # ✅ Handle image uploads
        images = self.request.FILES.getlist("images")  # Ensure images are received
        if images:
            for image in images:
                AnimalImage.objects.create(animal=animal, image=image)

        return animal  # ✅ Return the created instance

# Custom Permission Class
class RoleBasedPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = request.user.user_type
        view_name = view.__class__.__name__  # Use class name instead of basename

        # Production Data (POST = add)
        if view_name == 'ProductionDataListCreateView' and request.method == 'POST':
            return role in [User.FARMER, User.STAFF]  # Farmer (1), Staff (3)

        # Health Records (POST/PUT = add/edit)
        if view_name == 'HealthRecordListCreateView' and request.method in ['POST', 'PUT']:
            return role in [User.FARMER, User.VET]  # Farmer (1), Vet (2)

        # Reproductive History (POST/PUT = add/edit)
        if view_name == 'ReproductiveHistoryListCreateView' and request.method in ['POST', 'PUT']:
            return role in [User.FARMER, User.VET]  # Farmer (1), Vet (2)

        # Allow GET for all authenticated users
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        role = request.user.user_type
        if role == User.FARMER:
            return obj.animal.farm.owner == request.user  # Farmer owns the farm
        elif role == User.STAFF:
            return obj.animal.farm.staff.filter(id=request.user.id).exists()  # Staff assigned to farm
        elif role == User.VET:
            # Assuming vets are assigned to farms or animals via a relationship
            return obj.animal.farm.vets.filter(id=request.user.id).exists()  # Vet assigned to farm
        return False
# Existing Views

class DailyProductionTotalsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Step 1: Get all accessible farm IDs for this user
        accessible_farm_ids = Farm.objects.filter(
            Q(owner=user) |
            Q(farm_staff__user=user) |
            Q(vet_staff__user=user)
        ).values_list('id', flat=True)

        # Step 2: Get all animal IDs that belong to those farms
        accessible_animal_ids = Animal.objects.filter(
            farm__id__in=accessible_farm_ids
        ).values_list('id', flat=True)

        # Step 3: Parse dates from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date:
            start_date = timezone.now().date() - timedelta(days=6)
        else:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()

        if not end_date:
            end_date = timezone.now().date()
        else:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Step 4: Query production data only for accessible animals
        daily_totals = (
            ProductionData.objects
            .filter(animal_id__in=accessible_animal_ids, date__range=[start_date, end_date])
            .values('date')
            .annotate(
                total_milk_yield=Sum('milk_yield'),
                total_feed_consumption=Sum('feed_consumption'),
                total_scc=Sum('scc')
            )
            .order_by('date')
        )

        # Step 5: Format response
        response_data = [
            {
                'date': entry['date'].strftime('%b %d'),
                'total_milk_yield': float(entry['total_milk_yield'] or 0),
                'total_feed_consumption': float(entry['total_feed_consumption'] or 0),
                'total_scc': entry['total_scc'] or 0,
            }
            for entry in daily_totals
        ]

        return Response(response_data, status=status.HTTP_200_OK)

class HealthRecordRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes =  []  # Added IsAuthenticated
    lookup_field = 'id'  # Matches /health-records/<id>/
#IsAuthenticated, RoleBasedPermission
    def get_queryset(self):
        """
        Optionally filter queryset based on user permissions or animal ID.
        """
        user = self.request.user
        if hasattr(user, 'user_type'):  # Assuming user_type is a field on your User model
            if user.user_type == 3:  # Staff: read-only or limited access
                return HealthRecord.objects.filter(animal__farm__staff=user)
            return HealthRecord.objects.all()  # Farmers and Vets get full access
        return HealthRecord.objects.none()  # Default to no access if user_type missing

    def perform_update(self, serializer):
        """
        Custom logic before saving the update, if needed.
        """
        serializer.save()  # Default behavior; add custom logic here if required
    

class AnimalListView(generics.ListAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get farms the user is linked to
        owned_farms = Farm.objects.filter(owner=user)
        staff_farms = Farm.objects.filter(farm_staff__user=user)
        vet_farms = Farm.objects.filter(vet_staff__user=user)

        # Combine all accessible farm IDs
        accessible_farm_ids = owned_farms.union(staff_farms, vet_farms).values_list('id', flat=True)

        return Animal.objects.filter(farm__id__in=accessible_farm_ids).prefetch_related(
            'images', 'health_records', 'production_data', 'reproductive_history',
            'feed_management', 'financial_details', 'lactation_status', 'lifetime_stats', 'farm'
        )

class AnimalDetailView(generics.RetrieveAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        owned_farms = Farm.objects.filter(owner=user)
        staff_farms = Farm.objects.filter(farm_staff__user=user)
        vet_farms = Farm.objects.filter(vet_staff__user=user)

        accessible_farm_ids = owned_farms.union(staff_farms, vet_farms).values_list('id', flat=True)

        return Animal.objects.filter(farm__id__in=accessible_farm_ids).prefetch_related(
            'images', 'health_records', 'production_data', 'reproductive_history',
            'feed_management', 'financial_details', 'lactation_status', 'lifetime_stats', 'farm'
        )


class ProductionDataListCreateView(generics.ListCreateAPIView):
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer
    permission_classes = [RoleBasedPermission]  # Farmer, Staff can add

    def perform_create(self, serializer):
        serializer.save()
class HealthRecordListCreateView(generics.ListCreateAPIView):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [RoleBasedPermission]

    def perform_create(self, serializer):
        logger.info(f"HealthRecord POST data: {self.request.data}")
        animal_id = self.request.data.get('animal')
        if not animal_id:
            logger.error("No animal ID provided")
            raise serializers.ValidationError({"animal": "This field is required."})
        try:
            animal = Animal.objects.get(id=animal_id)
            instance = serializer.save(animal=animal)
            logger.info(f"Created HealthRecord: {instance.id}")
        except Animal.DoesNotExist:
            logger.error(f"Animal with ID {animal_id} not found")
            raise serializers.ValidationError({"animal": "Animal does not exist."})

class ReproductiveHistoryListCreateView(generics.ListCreateAPIView):
    queryset = ReproductiveHistory.objects.all()
    serializer_class = ReproductiveHistorySerializer
    permission_classes = [RoleBasedPermission]

    def perform_create(self, serializer):
        logger.info(f"ReproductiveHistory POST data: {self.request.data}")
        animal_id = self.request.data.get('animal')
        if not animal_id:
            logger.error("No animal ID provided")
            raise serializers.ValidationError({"animal": "This field is required."})
        try:
            animal = Animal.objects.get(id=animal_id)
            instance = serializer.save(animal=animal)
            logger.info(f"Created ReproductiveHistory: {instance.id}")
        except Animal.DoesNotExist:
            logger.error(f"Animal with ID {animal_id} not found")
            raise serializers.ValidationError({"animal": "Animal does not exist."})
