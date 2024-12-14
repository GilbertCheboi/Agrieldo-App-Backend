from django.urls import path
from .views import AvailableVetsView, FarmerProfileView

urlpatterns = [
    path('vets/available/', AvailableVetsView.as_view(), name='available-vets'),
    path('farmer/profile/', FarmerProfileView.as_view(), name='farmer_profile'),
]

