from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FarmViewSet,
    FarmStaffListView,
    AddFarmStaffView,
    RemoveFarmStaffView,
    FarmVetListView,
    AddFarmVetView,
    RemoveFarmVetView,
    get_farms,
    get_farm_by_id,
    FarmAnimalsView,
    get_vet_farms,  # ✅ new import
    get_staff_farms
)

# Router for standard CRUD endpoints
router = DefaultRouter()
router.register(r'farms', FarmViewSet, basename='farm')

urlpatterns = [
    # Base farm routes
    path('', include(router.urls)),

    # 👩‍🌾 Staff Management
    path('<int:farm_id>/staff/', FarmStaffListView.as_view(), name='farm-staff-list'),
    path('<int:farm_id>/add-staff/', AddFarmStaffView.as_view(), name="add-farm-staff"),
    path('<int:farm_id>/remove-staff/<int:user_id>/', RemoveFarmStaffView.as_view(), name="remove-farm-staff"),

    # 🧑‍⚕️ Vet Management
    path("<int:farm_id>/vets/", FarmVetListView.as_view(), name="farm-vet-list"),
    path("<int:farm_id>/add-vet/", AddFarmVetView.as_view(), name="add-farm-vet"),
    path("<int:farm_id>/remove-vet/<int:user_id>/", RemoveFarmVetView.as_view(), name="remove-farm-vet"),

    # 🧭 Farm listing & details
    path("get_farms/", get_farms, name="get_farms"),                # Farms owned by logged-in farmer
    path("get_farms/<int:pk>/", get_farm_by_id, name="farm-detail"),# Specific farm detail
    path("vet/farms/", get_vet_farms, name="get_vet_farms"),        # ✅ Farms assigned to logged-in vet
    path("staff/farms/", get_staff_farms, name="get_staff_farms"),  # ✅ New route for staff farms

    # 🐄 Farm animals
    path('<int:farm_id>/animals/', FarmAnimalsView.as_view(), name='farm-animals'),
]

