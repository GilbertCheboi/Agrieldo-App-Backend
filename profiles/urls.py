from django.urls import path
from .views import AvailableVetsView, FarmerProfileView, StaffProfileView,  LeadViewSet, update_lead

lead_list = LeadViewSet.as_view({'get': 'list', 'post': 'create'})
lead_detail = LeadViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

urlpatterns = [
    path('vets/available/', AvailableVetsView.as_view(), name='available-vets'),
    path('farmer/profile/', FarmerProfileView.as_view(), name='farmer_profile'),
    path('staff/profile/', StaffProfileView.as_view(), name='staff_profile'),

    path('leads/', lead_list, name='lead-list'),
    path('leads/<int:pk>/', lead_detail, name='lead-detail'),
    path('leads/update/<int:id>/', update_lead, name='update-lead'),  # Update the lead based on ID


]

