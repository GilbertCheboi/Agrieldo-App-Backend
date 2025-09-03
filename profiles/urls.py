from django.urls import path
from .views import FarmerProfileView, StaffProfileView, AvailableVetsView, AllVetsView, MyVetRequestListView, LeadViewSet, update_lead, VetRequestCreateView, VetRequestListView, UserProfileView, accept_vet_request, decline_vet_request
lead_list = LeadViewSet.as_view({'get': 'list', 'post': 'create'})
lead_detail = LeadViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})

urlpatterns = [
    path('farmer/profile/', FarmerProfileView.as_view(), name='farmer_profile'),
    path('staff/profile/', StaffProfileView.as_view(), name='staff_profile'),
    path('user/profile/', UserProfileView.as_view(), name='user-detail'),
    path('leads/', lead_list, name='lead-list'),
    path('leads/<int:pk>/', lead_detail, name='lead-detail'),
    path('leads/update/<int:id>/', update_lead, name='update-lead'),  # Update the lead based on ID
    path("vets/available/", AvailableVetsView.as_view(), name="available-vets"),
     path("vets/", AllVetsView.as_view(), name="all-vets"),
    path("vet/request/", VetRequestCreateView.as_view(), name="vet-request-create"),
    path("vet/requests/", VetRequestListView.as_view(), name="vet-request-list"),
    path("vet/requests/my/", MyVetRequestListView.as_view(), name="my-vet-requests"),

    path('vet/requests/<int:pk>/accept/', accept_vet_request, name='vet-request-accept'),
    path('vet/requests/<int:pk>/decline/', decline_vet_request, name='vet-request-decline'),
]

