from rest_framework import generics
from .models import Event
from .serializers import EventSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow public access

def user_role(request):
    user = request.user
    return Response({
        'is_staff': user.is_staff,
        'is_admin': user.is_superuser
    })

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]  # Make this view publicly accessible

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]  # Make this view publicly accessible


