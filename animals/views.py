from rest_framework import serializers  
from rest_framework.generics import ListCreateAPIView
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, Avg,  ExpressionWrapper, DecimalField, FloatField
from rest_framework.response import Response
from .models import Animal, HealthRecord, ProductionData, ReproductiveHistory, FeedManagement, FinancialDetails, LactationPeriod
from accounts.models import User
from .serializers import AnimalSerializer, HealthRecordSerializer, ProductionDataSerializer, ReproductiveHistorySerializer, FeedManagementSerializer, FinancialDetailsSerializer, LactationPeriodSerializer, DailyProductionSummarySerializer, DailyFinancialSerializer, DailyFeedVsMilkRevenueSerializer
from datetime import timedelta, datetime
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ( AnimalImage)
import logging
from django.db.models.functions import TruncDate
from collections import defaultdict

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
        if view_name in ['ProductionDataListCreateView', 'ProductionDataRetrieveUpdateView'] and request.method in ['POST', 'PUT']:
            return role in [User.FARMER, User.STAFF] # Farmer (1), Staff (3)

        # Health Records (POST/PUT = add/edit)
        if view_name == 'HealthRecordListCreateView' and request.method in ['POST', 'PUT']:
            return role in [User.FARMER, User.VET]  # Farmer (1), Vet (2)

        # # Reproductive History (POST/PUT = add/edit)
        # if view_name == 'ReproductiveHistoryListCreateView' and request.method in ['POST', 'PUT']:
        #     return role in [User.FARMER, User.VET]  # Farmer (1), Vet (2)

        # Reproductive History (POST/PUT = add/edit)
        if view_name in ['ReproductiveHistoryListCreateView', 'ReproductiveHistoryRetrieveUpdateView'] \
        and request.method in ['POST', 'PUT']:
            return role in [User.FARMER, User.VET]

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
            'feed_management', 'financial_details', 'lactation_periods', 'lifetime_stats', 'farm'
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
            'feed_management', 'financial_details', 'lactation_periods', 'lifetime_stats', 'farm'
        )

class MilkProductionCreateView(generics.ListCreateAPIView):
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class LactatingAnimalsListView(generics.ListAPIView):
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Get farms linked to the user
        owned_farms = Farm.objects.filter(owner=user)
        staff_farms = Farm.objects.filter(farm_staff__user=user)
        vet_farms = Farm.objects.filter(vet_staff__user=user)

        # Combine all accessible farm IDs
        accessible_farm_ids = owned_farms.union(staff_farms, vet_farms).values_list('id', flat=True)

        # Return lactating animals from accessible farms
        return Animal.objects.filter(
            farm__id__in=accessible_farm_ids,
            lactation_periods__is_milking=True
        ).distinct().prefetch_related(
            'images', 'health_records', 'production_data', 'reproductive_history',
            'feed_management', 'financial_details', 'lactation_periods', 'lifetime_stats', 'farm'
        )



class DailyMilkProductionSummaryView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self, request):
        # Filter production data by user
        summary = (
            ProductionData.objects.filter(animal__farm__owner=request.user)  # <-- Filter by authenticated user
            .values('date')
            .annotate(
                total_milk_yield=Sum('milk_yield'),
                total_revenue=Sum(ExpressionWrapper(F('milk_yield') * F('milk_price_per_liter'), output_field=DecimalField())),
                avg_price_per_liter=ExpressionWrapper(
                    Sum(ExpressionWrapper(F('milk_yield') * F('milk_price_per_liter'), output_field=DecimalField())) /
                    Sum(F('milk_yield')),
                    output_field=DecimalField()
                ),
                total_feed_consumption=Sum('feed_consumption'),
                avg_scc=Avg('scc'),
                avg_fat_percentage=Avg('fat_percentage'),
                avg_protein_percentage=Avg('protein_percentage'),
            )
        )

        serializer = DailyProductionSummarySerializer(summary, many=True)
        return Response(serializer.data)




class ProductionDataListCreateView(generics.ListCreateAPIView):
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer
    permission_classes = [RoleBasedPermission]

    def create(self, request, *args, **kwargs):
        logger.info(f"Received request data: {request.data}")
        if isinstance(request.data, list):
            logger.info("Processing as list")
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            logger.info("Processing as single object")
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ProductionDataRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer
    permission_classes = [RoleBasedPermission]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating production data with ID {kwargs.get('id')}")
        return super().update(request, *args, **kwargs)

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

class ReproductiveHistoryRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = ReproductiveHistory.objects.all()
    serializer_class = ReproductiveHistorySerializer
    permission_classes = [RoleBasedPermission]
    lookup_field = 'id'  # Ensure this matches your URL pattern

    def get_queryset(self):
        """
        Optionally filter based on user roles.
        """
        user = self.request.user
        if hasattr(user, 'user_type'):
            if user.user_type == 3:  # Staff
                return ReproductiveHistory.objects.filter(animal__farm__staff=user)
            return ReproductiveHistory.objects.all()
        return ReproductiveHistory.objects.none()

    def perform_update(self, serializer):
        logger.info(f"Updating ReproductiveHistory ID {self.kwargs.get('id')}")
        return serializer.save()


class FeedManagementListCreateView(generics.ListCreateAPIView):
    queryset = FeedManagement.objects.all()
    serializer_class = FeedManagementSerializer
    permission_classes = [RoleBasedPermission]  # Adjust as needed

    def perform_create(self, serializer):
        logger.info(f"FeedManagement POST data: {self.request.data}")
        animal_id = self.request.data.get('animal')
        if not animal_id:
            logger.error("No animal ID provided")
            raise serializers.ValidationError({"animal": "This field is required."})
        try:
            animal = Animal.objects.get(id=animal_id)
            instance = serializer.save(animal=animal)
            logger.info(f"Created FeedManagement: {instance.id}")
        except Animal.DoesNotExist:
            logger.error(f"Animal with ID {animal_id} not found")
            raise serializers.ValidationError({"animal": "Animal does not exist."})

class FinancialDetailsListCreateView(generics.ListCreateAPIView):
    queryset = FinancialDetails.objects.all()
    serializer_class = FinancialDetailsSerializer
    permission_classes = [RoleBasedPermission]  # Adjust as needed

    def perform_create(self, serializer):
        logger.info(f"FinancialDetails POST data: {self.request.data}")
        animal_id = self.request.data.get('animal')
        if not animal_id:
            logger.error("No animal ID provided")
            raise serializers.ValidationError({"animal": "This field is required."})
        try:
            animal = Animal.objects.get(id=animal_id)
            # Check if FinancialDetails already exists for this animal (since it's OneToOne)
            if FinancialDetails.objects.filter(animal=animal).exists():
                logger.error(f"FinancialDetails already exists for animal {animal_id}")
                raise serializers.ValidationError({"animal": "Financial details already exist for this animal."})
            instance = serializer.save(animal=animal)
            logger.info(f"Created FinancialDetails: {instance.id}")
        except Animal.DoesNotExist:
            logger.error(f"Animal with ID {animal_id} not found")
            raise serializers.ValidationError({"animal": "Animal does not exist."})



class LactationPeriodListCreateView(generics.ListCreateAPIView):
    serializer_class = LactationPeriodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        animal_id = self.kwargs.get('animal_id')
        return LactationPeriod.objects.filter(animal__id=animal_id, animal__owner=self.request.user)

    def perform_create(self, serializer):
        animal_id = self.kwargs.get('animal_id')
        animal = get_object_or_404(Animal, id=animal_id, owner=self.request.user)
        serializer.save(animal=animal)





class FinancialDataView(APIView):
    def get(self, request):
        # Define date range (e.g., last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Aggregate revenue from ProductionData
        revenue_data = (ProductionData.objects
                       .filter(date__range=[start_date, end_date])
                       .annotate(day=TruncDate('date'))
                       .values('day')
                       .annotate(total_revenue=Sum(F('milk_yield') * F('milk_price_per_liter')))
                       .order_by('day'))

        # Aggregate costs from FeedManagement
        feed_costs = (FeedManagement.objects
                     .filter(date__range=[start_date, end_date])
                     .annotate(day=TruncDate('date'))
                     .values('day')
                     .annotate(total_cost=Sum('total_cost'))
                     .order_by('day'))

        # Aggregate costs from ReproductiveHistory (only AI/Natural Breeding events)
        repro_costs = (ReproductiveHistory.objects
                      .filter(date__range=[start_date, end_date], event__in=['AI', 'Natural Breeding'])
                      .annotate(day=TruncDate('date'))
                      .values('day')
                      .annotate(total_cost=Sum('cost'))
                      .order_by('day'))

        # Aggregate costs from HealthRecord
        health_costs = (HealthRecord.objects
                       .filter(date__range=[start_date, end_date])
                       .annotate(day=TruncDate('date'))
                       .values('day')
                       .annotate(total_cost=Sum('cost'))
                       .order_by('day'))

        # Combine all data into a single daily breakdown
        daily_totals = defaultdict(lambda: {'total_cost': Decimal('0.00'), 'total_revenue': Decimal('0.00')})

        # Add revenue
        for entry in revenue_data:
            day = entry['day']
            daily_totals[day]['total_revenue'] += Decimal(str(entry['total_revenue'] or 0))

        # Add feed costs
        for entry in feed_costs:
            day = entry['day']
            daily_totals[day]['total_cost'] += Decimal(str(entry['total_cost'] or 0))

        # Add reproduction costs
        for entry in repro_costs:
            day = entry['day']
            daily_totals[day]['total_cost'] += Decimal(str(entry['total_cost'] or 0))

        # Add health costs
        for entry in health_costs:
            day = entry['day']
            daily_totals[day]['total_cost'] += Decimal(str(entry['total_cost'] or 0))

        # Format data for serialization
        formatted_data = [
            {'date': day, 'total_cost': totals['total_cost'], 'total_revenue': totals['total_revenue']}
            for day, totals in sorted(daily_totals.items())
        ]

        # Serialize and return
        serializer = DailyFinancialSerializer(formatted_data, many=True)
        return Response(serializer.data)


class DailyFeedVsMilkRevenueView(APIView):
    def get(self, request, farm_id):
        logger.info(f"Request for farm_id: {farm_id}, params: {request.query_params}")
        try:
            # Get end_date, defaulting to today, and ensure it's a date object
            end_date_param = request.query_params.get('end_date')
            if end_date_param:
                end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            else:
                end_date = datetime.today().date()

            # Get start_date, defaulting to 30 days before end_date
            start_date_param = request.query_params.get('start_date')
            if start_date_param:
                start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            else:
                start_date = end_date - timedelta(days=30)

            logger.info(f"Parsed start_date: {start_date}, end_date: {end_date}")

            # Get animals for the farm
            logger.info(f"Fetching animals for farm_id: {farm_id}")
            animals = Animal.objects.filter(farm_id=farm_id).values_list('id', flat=True)
            if not animals.exists():
                logger.warning(f"No animals found for farm_id: {farm_id}")
                return Response({"detail": "No animals found for this farm."}, status=status.HTTP_404_NOT_FOUND)
            logger.info(f"Found {len(animals)} animals")

            # Aggregate feed costs by date
            logger.info("Aggregating feed data")
            feed_data = (
                FeedManagement.objects
                .filter(animal__in=animals, date__range=[start_date, end_date])
                .values('date')
                .annotate(total_feed_cost=Sum('total_cost'))
                .order_by('date')
            )
            logger.info(f"Feed data: {list(feed_data)}")

            # Aggregate milk revenue by date
            logger.info("Aggregating milk data")
            milk_data = (
                ProductionData.objects
                .filter(animal__in=animals, date__range=[start_date, end_date])
                .values('date')
                .annotate(
                    total_milk_yield=Sum('milk_yield'),
                    avg_price=Avg('milk_price_per_liter')
                )
                .annotate(
                    total_revenue=ExpressionWrapper(
                        Sum('milk_yield') * Avg('milk_price_per_liter'),
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    )
                )
                .order_by('date')
            )
            logger.info(f"Milk data: {list(milk_data)}")

            # Combine data into a single response
            result = {}
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                result[date_str] = {'date': date_str, 'feed_cost': 0.0, 'milk_revenue': 0.0}
                current_date += timedelta(days=1)

            for entry in feed_data:
                date_str = entry['date'].strftime('%Y-%m-%d')
                result[date_str]['feed_cost'] = float(entry['total_feed_cost'])

            for entry in milk_data:
                date_str = entry['date'].strftime('%Y-%m-%d')
                result[date_str]['milk_revenue'] = float(entry['total_revenue'])

            response_data = list(result.values())
            serializer = DailyFeedVsMilkRevenueSerializer(response_data, many=True)
            logger.info("Data serialized successfully")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as ve:
            logger.error(f"ValueError: {str(ve)}")
            return Response({'error': f"Invalid date format: {str(ve)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class LactationPeriodRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LactationPeriod.objects.all()
    serializer_class = LactationPeriodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LactationPeriod.objects.filter(animal__owner=self.request.user)


class DailyFeedVsMilkView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, farm_id):
        user = request.user

        # Check farm access
        farm = get_object_or_404(
            Farm.objects.filter(
                Q(owner=user) |
                Q(farm_staff__user=user) |
                Q(vet_staff__user=user)
            ),
            id=farm_id
        )

        # Get animals in the farm
        animals = Animal.objects.filter(farm=farm).values_list('id', flat=True)

        # Get date range from query params or use last 7 days
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

        # Get daily milk and feed data
        daily_data = (
            ProductionData.objects
            .filter(animal_id__in=animals, date__range=[start_date, end_date])
            .values('date')
            .annotate(
                total_milk_yield=Sum('milk_yield'),
                total_feed_consumption=Sum('feed_consumption')
            )
            .order_by('date')
        )

        response_data = [
            {
                'date': entry['date'].strftime('%b %d'),
                'milk_yield': float(entry['total_milk_yield'] or 0),
                'feed_consumption': float(entry['total_feed_consumption'] or 0),
            }
            for entry in daily_data
        ]

        return Response(response_data, status=status.HTTP_200_OK)
