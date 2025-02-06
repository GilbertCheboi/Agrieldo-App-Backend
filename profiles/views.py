from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Vet
from .models import Farmer, Staff
from .serializers import FarmerSerializer
from .serializers import VetSerializer
from .utils import haversine
from rest_framework import viewsets

from rest_framework.decorators import api_view

from .models import Lead
from .serializers import LeadSerializer

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by('-created_at')
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

@api_view(['PUT'])
def update_lead(request, id):
    try:
        lead = Lead.objects.get(id=id)
    except Lead.DoesNotExist:
        return Response({'error': 'Lead not found'}, status=status.HTTP_404_NOT_FOUND)

    # Deserialize the request data
    serializer = LeadSerializer(lead, data=request.data, partial=True)
    
    if serializer.is_valid():
        # Save the updated lead
        serializer.save()
        return Response(serializer.data)
    else:
        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvailableVetsView(APIView):
    def post(self, request):
        # Farmer's location and search radius
        farmer_latitude = request.data.get('latitude')
        farmer_longitude = request.data.get('longitude')
        radius = request.data.get('radius', 50)  # default to 50 km

        if farmer_latitude is None or farmer_longitude is None:
            return Response({'error': 'Latitude and longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            radius = float(radius)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid radius provided. It must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Define the recent activity threshold (e.g., last 17 minutes)
        time_threshold = timezone.now() - timedelta(minutes=15)

        # Get available vets who have been active recently
        nearby_vets = []
        vets = Vet.objects.filter(is_available=True, last_active__gte=time_threshold)

        for vet in vets:
            vet_latitude = vet.user.latitude
            vet_longitude = vet.user.longitude

            if vet_latitude is None or vet_longitude is None:
                continue

            # Calculate distance between farmer and each vet
            distance = haversine(float(farmer_latitude), float(farmer_longitude), vet_latitude, vet_longitude)
            if distance <= radius:
                nearby_vets.append(vet)

        # Serialize and return the list of nearby vets
        if nearby_vets:
            serializer = VetSerializer(nearby_vets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No available vets found within the specified radius.'}, status=status.HTTP_404_NOT_FOUND)


class FarmerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the farmer profile for the logged-in user
            farmer = Farmer.objects.get(user=request.user)
            serializer = FarmerSerializer(farmer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Farmer.DoesNotExist:
            return Response({'error': 'Farmer profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            # Get the farmer profile for the logged-in user
            farmer = Farmer.objects.get(user=request.user)
            serializer = FarmerSerializer(farmer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Farmer.DoesNotExist:
            return Response({'error': 'Farmer profile not found.'}, status=status.HTTP_404_NOT_FOUND)



class StaffProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the farmer profile for the logged-in user
            staff = Staff.objects.get(user=request.user)
            serializer = StaffSerializer(staff)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Farmer.DoesNotExist:
            return Response({'error': 'Staff profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            # Get the farmer profile for the logged-in user
            staff = Staff.objects.get(user=request.user)
            serializer = StaffSerializer(farmer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff profile not found.'}, status=status.HTTP_404_NOT_FOUND)

