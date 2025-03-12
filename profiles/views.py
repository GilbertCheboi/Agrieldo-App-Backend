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
            staff = Staff.objects.get(user=request.user)
            serializer = StaffSerializer(staff)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:  # Fixed exception type
            return Response({'error': 'Staff profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            staff = Staff.objects.get(user=request.user)
            serializer = StaffSerializer(staff, data=request.data, partial=True)  # Fixed variable name
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff profile not found.'}, status=status.HTTP_404_NOT_FOUND)
