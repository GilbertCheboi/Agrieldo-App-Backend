from django.urls import path
from .consumers import FarmerLocationConsumer, VetLocationConsumer

websocket_urlpatterns = [
    path('ws/vet_location/<int:vet_id>/', VetLocationConsumer.as_asgi()),
    path('ws/farmer_location/<int:farmer_id>/', FarmerLocationConsumer.as_asgi()),
]

