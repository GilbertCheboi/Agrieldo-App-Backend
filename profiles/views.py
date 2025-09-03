# from rest_framework.permissions import IsAuthenticated
# from datetime import timedelta
# from django.utils import timezone
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Vet
# from .models import Farmer, Staff, Vet
# from .serializers import FarmerSerializer, VetRequestSerializer
# from .serializers import VetSerializer
# from rest_framework import viewsets, generics

# from rest_framework.decorators import api_view

# from .models import Lead
# from .serializers import LeadSerializer

# import math

# def haversine(lat1, lon1, lat2, lon2):
#     R = 6371  # Earth radius in km
#     dlat = math.radians(lat2 - lat1)
#     dlon = math.radians(lon2 - lon1)
#     a = (
#         math.sin(dlat / 2) ** 2
#         + math.cos(math.radians(lat1))
#         * math.cos(math.radians(lat2))
#         * math.sin(dlon / 2) ** 2
#     )
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     return R * c


# class LeadViewSet(viewsets.ModelViewSet):
#     queryset = Lead.objects.all().order_by('-created_at')
#     serializer_class = LeadSerializer
#     permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access

# @api_view(['PUT'])
# def update_lead(request, id):
#     try:
#         lead = Lead.objects.get(id=id)
#     except Lead.DoesNotExist:
#         return Response({'error': 'Lead not found'}, status=status.HTTP_404_NOT_FOUND)

#     # Deserialize the request data
#     serializer = LeadSerializer(lead, data=request.data, partial=True)
    
#     if serializer.is_valid():
#         # Save the updated lead
#         serializer.save()
#         return Response(serializer.data)
#     else:
#         # Return validation errors
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class FarmerProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             # Get the farmer profile for the logged-in user
#             farmer = Farmer.objects.get(user=request.user)
#             serializer = FarmerSerializer(farmer)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Farmer.DoesNotExist:
#             return Response({'error': 'Farmer profile not found.'}, status=status.HTTP_404_NOT_FOUND)

#     def put(self, request):
#         try:
#             # Get the farmer profile for the logged-in user
#             farmer = Farmer.objects.get(user=request.user)
#             serializer = FarmerSerializer(farmer, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Farmer.DoesNotExist:
#             return Response({'error': 'Farmer profile not found.'}, status=status.HTTP_404_NOT_FOUND)




# class StaffProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         try:
#             staff = Staff.objects.get(user=request.user)
#             serializer = StaffSerializer(staff)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Staff.DoesNotExist:  # Fixed exception type
#             return Response({'error': 'Staff profile not found.'}, status=status.HTTP_404_NOT_FOUND)

#     def put(self, request):
#         try:
#             staff = Staff.objects.get(user=request.user)
#             serializer = StaffSerializer(staff, data=request.data, partial=True)  # Fixed variable name
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Staff.DoesNotExist:
#             return Response({'error': 'Staff profile not found.'}, status=status.HTTP_404_NOT_FOUND)

# class AvailableVetsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             lat = request.data.get("latitude")
#             lon = request.data.get("longitude")
#             radius = request.data.get("radius", 15)  # default 15 km

#             if lat is None or lon is None:
#                 return Response(
#                     {"error": "latitude and longitude are required"},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             nearby_vets = []
#             for vet in Vet.objects.filter(is_available=True):  # assuming Vet has `is_available`
#                 if vet.latitude and vet.longitude:
#                     distance = haversine(float(lat), float(lon), vet.latitude, vet.longitude)
#                     if distance <= float(radius):
#                         nearby_vets.append(vet)

#             serializer = VetSerializer(nearby_vets, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class VetRequestCreateView(generics.CreateAPIView):
#     serializer_class = VetRequestSerializer
#     permission_classes = [permissions.IsAuthenticated]

# class VetRequestListView(generics.ListAPIView):
#     serializer_class = VetRequestSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # farmer can see their own requests
#         return VetRequest.objects.filter(farmer=self.request.user).order_by("-created_at")


from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Vet, Farmer, Staff, VetRequest, Lead
from .serializers import (
    FarmerSerializer,
    StaffSerializer,
    VetSerializer,
    VetRequestSerializer,
    LeadSerializer,
)
from rest_framework import viewsets, generics
from rest_framework.decorators import api_view
import math

from accounts.models import User
from .serializers import UserDetailSerializer
from rest_framework.parsers import MultiPartParser, FormParser


from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

# Haversine formula to calculate distance in km
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all().order_by("-created_at")
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]


@api_view(["PUT"])
def update_lead(request, id):
    try:
        lead = Lead.objects.get(id=id)
    except Lead.DoesNotExist:
        return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LeadSerializer(lead, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FarmerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            farmer = Farmer.objects.get(user=request.user)
            serializer = FarmerSerializer(farmer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Farmer.DoesNotExist:
            return Response(
                {"error": "Farmer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request):
        try:
            farmer = Farmer.objects.get(user=request.user)
            serializer = FarmerSerializer(farmer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Farmer.DoesNotExist:
            return Response(
                {"error": "Farmer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class StaffProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            staff = Staff.objects.get(user=request.user)
            serializer = StaffSerializer(staff)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Staff.DoesNotExist:
            return Response(
                {"error": "Staff profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request):
        try:
            staff = Staff.objects.get(user=request.user)
            serializer = StaffSerializer(staff, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Staff.DoesNotExist:
            return Response(
                {"error": "Staff profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class AvailableVetsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            lat = request.data.get("latitude")
            lon = request.data.get("longitude")
            radius = request.data.get("radius", 15)

            if lat is None or lon is None:
                return Response(
                    {"error": "latitude and longitude are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            nearby_vets = []
            for vet in Vet.objects.filter(is_available=True):
                if hasattr(vet, "latitude") and hasattr(vet, "longitude") and vet.latitude and vet.longitude:
                    distance = haversine(float(lat), float(lon), vet.latitude, vet.longitude)
                    if distance <= float(radius):
                        nearby_vets.append(vet)

            serializer = VetSerializer(nearby_vets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AllVetsView(generics.ListAPIView):
    """
    List all vets, regardless of availability or location.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vet.objects.all()
    serializer_class = VetSerializer

class VetRequestCreateView(generics.CreateAPIView):
    serializer_class = VetRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # handle images

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

class VetRequestListView(generics.ListAPIView):
    serializer_class = VetRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VetRequest.objects.filter(farmer=self.request.user).order_by("-created_at")

class MyVetRequestListView(generics.ListAPIView):
    serializer_class = VetRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get the Vet profile linked to the current user
        vet_instance = getattr(self.request.user, 'vet_profile', None)
        if not vet_instance:
            return VetRequest.objects.none()  # No vet profile → empty queryset

        # Return requests assigned to this vet
        return VetRequest.objects.filter(vet=vet_instance).order_by('-created_at')



class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # no need for ID in URL


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_vet_request(request, pk):
    vet_request = get_object_or_404(VetRequest, pk=pk)
    
    # Only assigned vet can accept
    if getattr(request.user, 'vet_profile', None) != vet_request.vet:
        return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if vet_request.status != 'pending':
        return Response({'detail': f'Request already {vet_request.status}.'}, status=status.HTTP_400_BAD_REQUEST)
    
    vet_request.status = 'accepted'
    vet_request.save()
    return Response({'detail': 'Vet request accepted.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def decline_vet_request(request, pk):
    vet_request = get_object_or_404(VetRequest, pk=pk)
    
    # Only assigned vet can decline
    if getattr(request.user, 'vet_profile', None) != vet_request.vet:
        return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

    if vet_request.status != 'pending':
        return Response({'detail': f'Request already {vet_request.status}.'}, status=status.HTTP_400_BAD_REQUEST)
    
    vet_request.status = 'rejected'
    vet_request.save()
    return Response({'detail': 'Vet request declined.'}, status=status.HTTP_200_OK)
