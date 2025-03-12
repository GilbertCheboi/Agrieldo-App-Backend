# sheep_app/views.py
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Sheep, SheepHealthRecord, SheepReproduction, SheepProduction, SheepImage, SheepType
from .serializers import (
    SheepSerializer, SheepHealthRecordSerializer,
    SheepReproductionSerializer, SheepProductionSerializer,
    SheepImageSerializer, SheepTypeSerializer
)

# Sheep Views
class SheepListCreateView(ListCreateAPIView):
    serializer_class = SheepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        farm_id = self.request.query_params.get('farm_id', None)
        queryset = Sheep.objects.filter(farm__owner=self.request.user)
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        return queryset

class SheepDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SheepSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Sheep.objects.filter(farm__owner=self.request.user)

# Sheep Health Record Views
class SheepHealthRecordListCreateView(ListCreateAPIView):
    serializer_class = SheepHealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sheep_id = self.request.query_params.get('sheep_id', None)
        queryset = SheepHealthRecord.objects.filter(sheep__farm__owner=self.request.user)
        if sheep_id:
            queryset = queryset.filter(sheep_id=sheep_id)
        return queryset

class SheepHealthRecordDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SheepHealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SheepHealthRecord.objects.filter(sheep__farm__owner=self.request.user)

# Sheep Reproduction Views
class SheepReproductionListCreateView(ListCreateAPIView):
    serializer_class = SheepReproductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sheep_id = self.request.query_params.get('sheep_id', None)
        queryset = SheepReproduction.objects.filter(sheep__farm__owner=self.request.user)
        if sheep_id:
            queryset = queryset.filter(sheep_id=sheep_id)
        return queryset

class SheepReproductionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SheepReproductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SheepReproduction.objects.filter(sheep__farm__owner=self.request.user)

# Sheep Production Views
class SheepProductionListCreateView(ListCreateAPIView):
    serializer_class = SheepProductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sheep_id = self.request.query_params.get('sheep_id', None)
        queryset = SheepProduction.objects.filter(sheep__farm__owner=self.request.user)
        if sheep_id:
            queryset = queryset.filter(sheep_id=sheep_id)
        return queryset

class SheepProductionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SheepProductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SheepProduction.objects.filter(sheep__farm__owner=self.request.user)

# Sheep Image Views
class SheepImageListCreateView(ListCreateAPIView):
    serializer_class = SheepImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sheep_id = self.request.query_params.get('sheep_id', None)
        queryset = SheepImage.objects.filter(sheep__farm__owner=self.request.user)
        if sheep_id:
            queryset = queryset.filter(sheep_id=sheep_id)
        return queryset

class SheepImageDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SheepImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SheepImage.objects.filter(sheep__farm__owner=self.request.user)

# Sheep Type Views
class SheepTypeListCreateView(ListCreateAPIView):
    serializer_class = SheepTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = SheepType.objects.all()  # No ownership filter, global resource

class SheepTypeDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SheepTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = SheepType.objects.all()
