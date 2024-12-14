# vet_requests/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:farmer_id>/', views.request_vet, name='request_vet'),
    path('respond/<int:vet_request_id>/', views.respond_to_request, name='respond_to_request'),
]

