
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics

from rest_framework import viewsets
from .models import Machinery,  MaintenanceLog, FuelLog, SparePart, Alert
from .serializers import (
    MachinerySerializer,  MaintenanceLogSerializer,
    FuelLogSerializer, SparePartSerializer, AlertSerializer
)

from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MachineryUsageLog
from .serializers import MachineryUsageLogSerializer
from rest_framework.permissions import IsAuthenticated

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
