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


class VetRequestCreateView(generics.CreateAPIView):
    serializer_class = VetRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


class VetRequestListView(generics.ListAPIView):
    serializer_class = VetRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VetRequest.objects.filter(farmer=self.request.user).order_by("-created_at")
