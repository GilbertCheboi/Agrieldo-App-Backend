from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import MarketListing
from .serializers import (
    MarketListingSerializer,
    CreateListingSerializer
)
from animals.models import Animal


class CreateListingView(generics.CreateAPIView):
    serializer_class = CreateListingSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        animal_id = request.data.get('animal')

        if not animal_id:
            return Response({"error": "Animal ID is required"}, status=400)

        try:
            animal = Animal.objects.get(id=animal_id)
        except Animal.DoesNotExist:
            return Response({"error": "Animal not found"}, status=404)

        # Ensure only the owner can list
        if animal.owner != request.user:
            return Response({"error": "You are not the owner of this animal"}, status=403)

        # If already listed
        if hasattr(animal, 'market_listing'):
            listing = animal.market_listing
            listing.status = 'active'
            listing.save()
            return Response({"message": "Animal relisted successfully"}, status=200)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = serializer.save(
            seller=request.user,
            animal=animal,
            status='active'
        )

        return Response(MarketListingSerializer(listing).data, status=201)


class MarketListingListView(generics.ListAPIView):
    queryset = MarketListing.objects.filter(status='active').order_by('-created_at')
    serializer_class = MarketListingSerializer


class MarketListingDetailView(generics.RetrieveAPIView):
    queryset = MarketListing.objects.all()
    serializer_class = MarketListingSerializer


class ToggleListingStatusView(generics.UpdateAPIView):
    queryset = MarketListing.objects.all()
    serializer_class = MarketListingSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        listing = self.get_object()

        if listing.seller != request.user:
            return Response({"error": "Not allowed"}, status=403)

        new_status = request.data.get("status")
        if new_status not in ['active', 'hidden', 'sold']:
            return Response({"error": "Invalid status"}, status=400)

        listing.status = new_status
        listing.save()

        return Response(MarketListingSerializer(listing).data)

