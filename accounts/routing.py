from django.urls import path
from .consumers import UserLocationConsumer

websocket_urlpatterns = [
    path('ws/location/<int:user_id>/', UserLocationConsumer.as_asgi()),
]

