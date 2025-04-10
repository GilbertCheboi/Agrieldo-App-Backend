# subscriptions/views.py

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Subscription, Package
from .serializers import SubscriptionSerializer, PackageSerializer
from rest_framework.response import Response
from rest_framework import status

class SubscriptionListCreateView(ListCreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return subscriptions owned by the authenticated user
        return Subscription.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Set the authenticated user as the subscription owner
        serializer.save(owner=self.request.user)
    
class LatestSubscriptionView(RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        latest_subscription = Subscription.objects.filter(owner=request.user).order_by('-created_at').first()
        if latest_subscription:
            serializer = self.get_serializer(latest_subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "No subscription found."}, status=status.HTTP_404_NOT_FOUND)    

class PackageListView(ListAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]  # Or [IsAuthenticated] if you want to restrict