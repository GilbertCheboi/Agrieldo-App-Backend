# vet_requests/urls.py

from django.urls import path
from .views import VetRequestCreateView

urlpatterns = [
    path('request/', VetRequestCreateView.as_view(), name='vet_request_create'),
]

