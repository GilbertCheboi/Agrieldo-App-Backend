from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import NVR, Stream, JanusStream
from .serializers import NVRSerializer, StreamSerializer, JanusStreamSerializer

class IsFarmerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the farmer of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the farmer of the NVR
        return obj.farmer == request.user

class NVRViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing NVRs
    """
    queryset = NVR.objects.all()
    serializer_class = NVRSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmerOrReadOnly]

    def perform_create(self, serializer):
        # Automatically associate the NVR with the logged-in farmer
        serializer.save(farmer=self.request.user)

    def get_queryset(self):
        # Only return NVRs owned by the logged-in farmer
        return self.queryset.filter(farmer=self.request.user)

class StreamViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing streams
    """
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmerOrReadOnly]

    def perform_create(self, serializer):
        # Ensure the stream is associated with an NVR owned by the farmer
        nvr = serializer.validated_data['nvr']
        if nvr.farmer != self.request.user:
            raise permissions.PermissionDenied("You don't have permission to add streams to this NVR.")
        serializer.save()

    def get_queryset(self):
        # Only return streams associated with the farmer's NVRs
        return self.queryset.filter(nvr__farmer=self.request.user)

class JanusStreamViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing Janus streams
    """
    queryset = JanusStream.objects.all()
    serializer_class = JanusStreamSerializer
    permission_classes = [permissions.IsAuthenticated, IsFarmerOrReadOnly]

    def perform_create(self, serializer):
        # Ensure the JanusStream is associated with a Stream owned by the farmer
        stream = serializer.validated_data['stream']
        if stream.nvr.farmer != self.request.user:
            raise permissions.PermissionDenied("You don't have permission to add Janus streams to this Stream.")
        serializer.save()

    def get_queryset(self):
        # Only return Janus streams associated with the farmer's streams
        return self.queryset.filter(stream__nvr__farmer=self.request.user)

    @action(detail=True, methods=['get'])
    def get_janus_details(self, request, pk=None):
        """
        Custom action to retrieve Janus stream details for a specific stream.
        """
        janus_stream = self.get_object()
        return Response({
            "janus_room_id": janus_stream.janus_room_id,
            "janus_server_url": janus_stream.janus_server_url,
        })
