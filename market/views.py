from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Auction
from .serializers import AuctionSerializer
from animals.models import Animal
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework import status


@api_view(['POST'])
def create_auction(request, animal_id):
    try:
        # Get the animal object
        animal = Animal.objects.get(id=animal_id)
    except Animal.DoesNotExist:
        return Response({'error': 'Animal not found'}, status=404)

    # Prepare the auction data, using animal.id as a foreign key reference
    auction_data = {
        'animal': animal.id,  # Pass only the animal's primary key (id), not the full object
        'price': animal.price,  # Default price from the animal model (can be overridden)
        'description': request.data.get('description', 'A healthy cow ready for sale!'),
        'auction_end_date': request.data.get('auction_end_date', '2024-12-31'),
        'location': request.data.get('location', 'Farm 7, Rural Area'),
    }

    # Create the serializer and validate the data
    serializer = AuctionSerializer(data=auction_data)
    if serializer.is_valid():
        # Save the auction if the data is valid
        serializer.save()
        return Response(serializer.data, status=201)  # Return the newly created auction
    else:
        # Log validation errors for debugging
        print("Validation errors:", serializer.errors)  # Log errors for debugging
        return Response(serializer.errors, status=400)


class AuctionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auctions = Auction.objects.filter(auction_end_date__gte=timezone.now().date())

        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)

@api_view(['DELETE'])
def remove_auction(request, pk):
    try:
        auction = Auction.objects.get(pk=pk)
    except Auction.DoesNotExist:
        return Response({'detail': 'Auction not found'}, status=status.HTTP_404_NOT_FOUND)

    auction.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
