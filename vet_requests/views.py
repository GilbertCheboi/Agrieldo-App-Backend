# vet_requests/views.py
from django.contrib.gis.geos import Point

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from profiles.models import Farmer, Vet
from .models import VetRequest
from .utils import find_closest_vet, send_notification
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import VetRequestSerializer

class VetRequestCreateView(APIView):
    def post(self, request, *args, **kwargs):
        farmer_id = request.user.id  # Assuming the user is authenticated

        # Ensure description is in the request data
        description = request.data.get('description')
        if not description:
            return Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)

        service_type = request.data.get('serviceType')
        if not service_type:
            return Response({'error': 'Service Type is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Add farmer_id to the request data
        request.data['farmer'] = farmer_id

        serializer = VetRequestSerializer(data=request.data)
        if serializer.is_valid():
            vet_request = serializer.save()
            return Response({
                'message': 'Vet request successful.',
                'vet_id': vet_request.id,
                'status': vet_request.status
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def request_vet(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    closest_vet = find_closest_vet(farmer.location_latitude, farmer.location_longitude)

    if closest_vet:
        vet_request = VetRequest.objects.create(farmer=farmer, vet=closest_vet)
        send_notification(closest_vet, "New Vet Request", "A farmer needs your assistance.")
        return Response({"message": "Request sent to the closest vet."}, status=status.HTTP_200_OK)
    else:
        return Response({"message": "No vets available."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def respond_to_request(request, vet_request_id):
    vet_request = get_object_or_404(VetRequest, id=vet_request_id)
    action = request.data.get("action")

    if action == "accept":
        vet_request.status = "accepted"
        vet_request.save()
        send_notification(vet_request.farmer, "Vet Request Accepted", "A vet has accepted your request.")
        return Response({"message": "Request accepted"}, status=status.HTTP_200_OK)
    elif action == "decline":
        vet_request.status = "declined"
        vet_request.save()
        send_notification(vet_request.farmer, "Vet Request Declined", "The assigned vet declined the request.")
        return Response({"message": "Request declined, reassigning"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid action"}, status=status.HTTP)
