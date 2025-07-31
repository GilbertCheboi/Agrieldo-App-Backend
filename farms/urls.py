from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmViewSet, FarmStaffListView, AddFarmStaffView, RemoveFarmStaffView, get_farms, get_farm_by_id, FarmVetListView, AddFarmVetView, RemoveFarmVetView, FarmAnimalsView


router = DefaultRouter()
router.register(r'farms', FarmViewSet, basename='farm')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:farm_id>/staff/', FarmStaffListView.as_view(), name='farm-staff-list'),
    path('<int:farm_id>/add-staff/', AddFarmStaffView.as_view(), name="add-farm-staff"),
    path('<int:farm_id>/remove-staff/<int:user_id>/', RemoveFarmStaffView.as_view(), name="remove-farm-staff"),
    path("<int:farm_id>/vets/", FarmVetListView.as_view(), name="farm-vet-list"),
    path("<int:farm_id>/add-vet/", AddFarmVetView.as_view(), name="add-farm-vet"),
    path("<int:farm_id>/remove-vet/<int:user_id>/", RemoveFarmVetView.as_view(), name="remove-farm-vet"),
    path("get_farms/", get_farms, name="get_farms"),  # List farms owned or managed by the user
    path("get_farms/<int:pk>/", get_farm_by_id, name="farm-detail"),  # List farms owned or managed by the user

    path('<int:farm_id>/animals/', FarmAnimalsView.as_view(), name='farm-animals'),




]

