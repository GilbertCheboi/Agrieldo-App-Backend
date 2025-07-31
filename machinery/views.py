
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view
from geopy.distance import geodesic
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import viewsets
from .models import Machinery,  MaintenanceLog, FuelLog, SparePart, Alert, MachineryVendorApplication, MachineryOrder
from .serializers import (
    MachinerySerializer,  MaintenanceLogSerializer,
    FuelLogSerializer, SparePartSerializer, AlertSerializer, MachineryVendorApplicationSerializer, MachineryOrderSerializer, MachineryOrderCreateSerializer
)

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MachineryUsageLog
from .serializers import MachineryUsageLogSerializer
from rest_framework.permissions import IsAuthenticated

from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance in kilometers.
    """
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

class MachineryUsageLogsView(APIView):
    def get(self, request, machinery_id):
        logs = MachineryUsageLog.objects.filter(machinery_id=machinery_id)
        serializer = MachineryUsageLogSerializer(logs, many=True)
        return Response(serializer.data)

class MachineryViewSet(viewsets.ModelViewSet):
    queryset = Machinery.objects.all()
    serializer_class = MachinerySerializer
    parser_classes = [MultiPartParser, FormParser]  # ✅ Allows image uploads
    permission_classes = [IsAuthenticated]  # ✅ Ensures authentication

    def perform_create(self, serializer):
        print(f"DEBUG: request.user = {self.request.user}")  # 🔍 Debugging step
        serializer.save(owner=self.request.user)  # ✅ Assigns owner automatically



class MaintenanceLogListCreateView(generics.ListCreateAPIView):
    serializer_class = MaintenanceLogSerializer

    def get_queryset(self):
        return MaintenanceLog.objects.filter(machinery_id=self.kwargs["machinery_id"])

class MaintenanceLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer

# Fuel Logs
class FuelLogListCreateView(generics.ListCreateAPIView):
    serializer_class = FuelLogSerializer

    def get_queryset(self):
        return FuelLog.objects.filter(machinery_id=self.kwargs["machinery_id"])

class FuelLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FuelLog.objects.all()
    serializer_class = FuelLogSerializer

# Spare Parts
class SparePartListCreateView(generics.ListCreateAPIView):
    serializer_class = SparePartSerializer

    def get_queryset(self):
        return SparePart.objects.filter(machinery_id=self.kwargs["machinery_id"])

class SparePartDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer

# Alerts
class AlertListCreateView(generics.ListCreateAPIView):
    serializer_class = AlertSerializer

    def get_queryset(self):
        return Alert.objects.filter(machinery_id=self.kwargs["machinery_id"])

class AlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

# View to create new vendor application
class MachineryVendorApplicationCreateView(generics.CreateAPIView):
    queryset = MachineryVendorApplication.objects.all()
    serializer_class = MachineryVendorApplicationSerializer

# View to list active and approved vendor applications
class ActiveApprovedVendorListView(generics.ListAPIView):
    queryset = MachineryVendorApplication.objects.filter(approved=True, is_active=True)
    serializer_class = MachineryVendorApplicationSerializer


@api_view(['GET'])
def nearby_machinery(request):
    """
    GET params:
      - type:      machine type, e.g. 'tractor' (case‑insensitive)
      - lat, lng:  user coords
      - radius_km: optional radius in km (default 5)

    Returns JSON:
      { results: [ { id, name, phone_number, type_of_machine,
                     model, distance_km, latitude, longitude, submitted_at }, … ] }
    """
    type_ = request.GET.get('type')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = float(request.GET.get('radius_km', 5.0))

    if not (type_ and lat and lng):
        return JsonResponse({'error': 'Missing parameters: type, lat, and lng are required.'}, status=400)

    try:
        user_lat = float(lat)
        user_lng = float(lng)
    except ValueError:
        return JsonResponse({'error': 'Invalid lat/lng values.'}, status=400)

    # only approved & active vendor applications
    vendors = MachineryVendorApplication.objects.filter(
        type_of_machine__iexact=type_,
        approved=True,
        is_active=True
    )

    results = []
    for v in vendors:
        if v.latitude is None or v.longitude is None:
            continue

        dist_km = haversine(user_lat, user_lng, v.latitude, v.longitude)
        if dist_km <= radius:
            results.append({
                'id': v.id,
                'name': v.name,
                'phone_number': v.phone_number,
                'type_of_machine': v.type_of_machine,
                'model': v.model,
                'price_per_day': float(v.price_per_day),
                'distance_km': round(dist_km, 2),
                'latitude': v.latitude,
                'longitude': v.longitude,
                'submitted_at': v.submitted_at.isoformat(),
            })

    return JsonResponse({'results': results})

@api_view(['PATCH'])
def update_my_location(request):
    """
    PATCH body: { "latitude": <float>, "longitude": <float> }
    Only the logged-in user’s own, approved & active application is updated.
    """
    user = request.user
    if not user or not user.is_authenticated:
        return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        vendor_app = MachineryVendorApplication.objects.get(
            user=user,
            approved=True,
            is_active=True
        )
    except MachineryVendorApplication.DoesNotExist:
        return Response(
            {'detail': 'No active, approved vendor application found for this user.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Only update lat/lng
    serializer = MachineryVendorApplicationSerializer(
        vendor_app,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MachineryOrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data

        # 1. Look up the machinery application
        try:
            machinery_app = MachineryVendorApplication.objects.get(id=data.get("machinery"))
        except MachineryVendorApplication.DoesNotExist:
            return Response({"machinery": "Not found"}, status=404)

        if not machinery_app.user:
            return Response({"machinery": "No user attached to this listing"}, status=400)

        # 2. Validate input fields
        serializer = MachineryOrderCreateSerializer(data=data)
        if not serializer.is_valid():
            # send back exactly what failed
            return Response(serializer.errors, status=400)

        # 3. Create the order, injecting vendor & machinery
        order = serializer.save(
            vendor=machinery_app.user,
            machinery=machinery_app,
        )

        # 4. Deactivate the listing
        machinery_app.is_active = False
        machinery_app.save()

        # 5. Return the full order back
        out = MachineryOrderSerializer(order)
        return Response(out.data, status=status.HTTP_201_CREATED)