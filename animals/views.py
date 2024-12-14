from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ( Animal, Dairy_Cow, Beef_Cow, Sheep,
Goat,
DairyMedicalRecord,
BeefMedicalRecord,
SheepMedicalRecord,
GoatMedicalRecord,
)

from .serializers import (
    AnimalSerializer,
    DairyCowSerializer,
    BeefCowSerializer,
    SheepSerializer,
    GoatSerializer,
    DairyMedicalRecordSerializer,
    BeefMedicalRecordSerializer,
    SheepMedicalRecordSerializer,
    GoatMedicalRecordSerializer,

)
import logging

logger = logging.getLogger(__name__)
# View for listing all animals or creating a new animal
class AnimalListCreateView(generics.ListCreateAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

# View for retrieving, updating, or deleting a specific animal
class AnimalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

# Views for each specific animal type can also be created similarly
class DairyCowListCreateView(generics.ListCreateAPIView):
    serializer_class = DairyCowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method filters the query to only return dairy cows belonging to the logged-in user.
        """
        return Dairy_Cow.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        This method saves the dairy cow with the current authenticated user as the owner.
        """
        serializer.save(owner=self.request.user)

class DairyCowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dairy_Cow.objects.all()
    serializer_class = DairyCowSerializer
    permission_classes = [IsAuthenticated]

class DairyMedicalRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = DairyMedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        dairy_cow_id = self.kwargs['pk']
        logger.debug(f"Fetching medical records for Dairy Cow ID: {dairy_cow_id}")
        queryset = DairyMedicalRecord.objects.filter(animal__id=dairy_cow_id)
        logger.debug(f"Queryset: {queryset}")
        return queryset

    def perform_create(self, serializer):
        serializer.save(veterinarian=self.request.user)

class BeefCowListCreateView(generics.ListCreateAPIView):
    queryset = Beef_Cow.objects.all()
    serializer_class = BeefCowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BeefCowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Beef_Cow.objects.all()
    serializer_class = BeefCowSerializer
    permission_classes = [IsAuthenticated]

class BeefMedicalRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = BeefMedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the dairy cow based on the primary key (pk) passed in the URL
        beef_cow_id = self.kwargs['pk']
        return BeefMedicalRecord.objects.filter(animal__id=beef_cow_id)

    def perform_create(self, serializer):
        # Automatically set the veterinarian to the current user
        serializer.save(veterinarian=self.request.user)

class SheepListCreateView(generics.ListCreateAPIView):
    queryset = Sheep.objects.all()
    serializer_class = SheepSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SheepDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sheep.objects.all()
    serializer_class = SheepSerializer
    permission_classes = [IsAuthenticated]

class SheepMedicalRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = SheepMedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the dairy cow based on the primary key (pk) passed in the URL
        sheep_id = self.kwargs['pk']
        return SheepMedicalRecord.objects.filter(animal__id=sheep_id)

    def perform_create(self, serializer):
        # Automatically set the veterinarian to the current user
        serializer.save(veterinarian=self.request.user)

class GoatListCreateView(generics.ListCreateAPIView):
    queryset = Goat.objects.all()
    serializer_class = GoatSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class GoatDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Goat.objects.all()
    serializer_class = GoatSerializer
    permission_classes = [IsAuthenticated]

class GoatMedicalRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = GoatMedicalRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter medical records by the animal ID passed in the URL
        animal_id = self.kwargs['pk']
        return GoatMedicalRecord.objects.filter(animal_id=goat_id)

    def perform_create(self, serializer):
        # Automatically assign the authenticated user as the veterinarian
        serializer.save(veterinarian=self.request.user)
