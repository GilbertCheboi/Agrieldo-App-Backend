from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Farm, FarmStaff, FarmVet
from .serializers import FarmSerializer, FarmStaffSerializer, VetStaffSerializer
from .permissions import IsFarmerOrReadOnly
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from animals.models import Animal
from animals.serializers import AnimalSerializer  # ✅ same here
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


User = get_user_model()

class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # handle images and JSON

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Farm.objects.all()

        if getattr(user, "user_type", None) == 1:  # FARMER
            return Farm.objects.filter(owner=user)

        if getattr(user, "user_type", None) == 3:  # STAFF
            return Farm.objects.filter(staff=user)

        return Farm.objects.none()

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if user.is_superuser:
            return obj

        if obj.owner == user or user in obj.staff.all():
            return obj

        raise PermissionDenied("You do not have permission to access this farm.")

    def perform_create(self, serializer):
        user = self.request.user
        # allow only farmers and superusers to create farms
        if user.is_superuser or getattr(user, "user_type", None) == 1:
            serializer.save(owner=user)
            return

        raise PermissionDenied("Only farmers may create farms.")

class FarmStaffListView(generics.ListAPIView):
    """
    API to list all staff members assigned to a farm.
    """
    serializer_class = FarmStaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, farm_id):
        farm = get_object_or_404(Farm, id=farm_id)
        staff_members = FarmStaff.objects.filter(farm=farm)
        serializer = self.get_serializer(staff_members, many=True)
        return Response(serializer.data)


class AddFarmStaffView(APIView):
    """
    API to add a user as staff to a farm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, farm_id):
        farm = get_object_or_404(Farm, id=farm_id)

        # Ensure only the farm owner can add staff
        if farm.owner != request.user:
            return Response({"error": "You are not authorized to add staff to this farm."},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the user exists
        user = get_object_or_404(User, id=user_id)

        # Prevent adding the farm owner as staff
        if user == farm.owner:
            return Response({"error": "The farm owner cannot be added as staff."}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to farm staff (avoid duplicate entries)
        staff, created = FarmStaff.objects.get_or_create(farm=farm, user=user)

        return Response({
            "message": "Staff member added successfully.",
            "staff": FarmStaffSerializer(staff).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RemoveFarmStaffView(APIView):
    """
    API to remove a staff member from a farm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, farm_id, user_id):
        farm = get_object_or_404(Farm, id=farm_id)

        # Ensure only the farm owner can remove staff
        if farm.owner != request.user:
            return Response({"error": "You are not authorized to remove staff from this farm."},
                            status=status.HTTP_403_FORBIDDEN)

        # Ensure the user exists
        user = get_object_or_404(User, id=user_id)

        # Check if the user is part of the staff
        staff = FarmStaff.objects.filter(farm=farm, user=user).first()
        if not staff:
            return Response({"error": "User is not a staff member of this farm."}, status=status.HTTP_400_BAD_REQUEST)

        # Remove staff
        staff.delete()
        return Response({"message": "Staff member removed successfully."}, status=status.HTTP_200_OK)


class FarmVetListView(generics.ListAPIView):
    """
    API to list all vet staff assigned to a farm.
    """
    serializer_class = VetStaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, farm_id):
        farm = get_object_or_404(Farm, id=farm_id)
        vets = FarmVet.objects.filter(farm=farm)
        serializer = self.get_serializer(vets, many=True)
        return Response(serializer.data)


class AddFarmVetView(APIView):
    """
    API to add a user as a vet staff to a farm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, farm_id):
        farm = get_object_or_404(Farm, id=farm_id)

        # Only owner can add vets
        if farm.owner != request.user:
            return Response({"error": "You are not authorized to add vets to this farm."},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        if user == farm.owner:
            return Response({"error": "The farm owner cannot be added as vet staff."}, status=status.HTTP_400_BAD_REQUEST)

        vet, created = FarmVet.objects.get_or_create(farm=farm, user=user)

        return Response({
            "message": "Vet staff added successfully.",
            "vet": VetStaffSerializer(vet).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RemoveFarmVetView(APIView):
    """
    API to remove a vet staff from a farm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, farm_id, user_id):
        farm = get_object_or_404(Farm, id=farm_id)

        if farm.owner != request.user:
            return Response({"error": "You are not authorized to remove vet staff from this farm."},
                            status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, id=user_id)
        vet = FarmVet.objects.filter(farm=farm, user=user).first()
        if not vet:
            return Response({"error": "User is not a vet staff member of this farm."}, status=status.HTTP_400_BAD_REQUEST)

        vet.delete()
        return Response({"message": "Vet staff member removed successfully."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_farms(request):
    """Return only farms owned by the authenticated user."""
    farms = Farm.objects.filter(owner=request.user)  # Assuming `owner` is the farm owner field
    serializer = FarmSerializer(farms, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_farm_by_id(request, pk):
    """
    Return the farm with the given id that is owned by the authenticated user.
    """
    try:
        farm = Farm.objects.get(pk=pk, owner=request.user)
    except Farm.DoesNotExist:
        return Response({"error": "Farm not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

    serializer = FarmSerializer(farm)
    return Response(serializer.data)

class FarmAnimalsView(APIView):
    """
    Return all animals for a specific farm if the user has access.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, farm_id):
        farm = get_object_or_404(Farm, id=farm_id)

        # Ensure the user has access to the farm
        is_owner = farm.owner == request.user
        is_staff = FarmStaff.objects.filter(farm=farm, user=request.user).exists()
        is_vet = FarmVet.objects.filter(farm=farm, user=request.user).exists()

        if not (is_owner or is_staff or is_vet):
            return Response({"error": "You are not authorized to view animals on this farm."},
                            status=status.HTTP_403_FORBIDDEN)

        animals = Animal.objects.filter(farm=farm).prefetch_related(
            'images', 'health_records', 'production_data', 'reproductive_history',
            'feed_management', 'financial_details', 'lactation_periods', 'lifetime_stats'
        )
        serializer = AnimalSerializer(animals, many=True)
        return Response(serializer.data)