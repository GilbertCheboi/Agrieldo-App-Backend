from django.urls import path
from .views import (
    MachineryViewSet,     MaintenanceLogListCreateView, MaintenanceLogDetailView,
    FuelLogListCreateView, FuelLogDetailView,
    SparePartListCreateView, SparePartDetailView,
    AlertListCreateView, AlertDetailView,  MachineryUsageLogsView
)

urlpatterns = [
    path('', MachineryViewSet.as_view({'get': 'list', 'post': 'create'}), name='machinery-list'),
    path('<int:pk>/', MachineryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='machinery-detail'),


    path("<int:machinery_id>/maintenanceLogs/", MaintenanceLogListCreateView.as_view(), name="maintenance-log-list"),
    path("maintenanceLogs/<int:pk>/", MaintenanceLogDetailView.as_view(), name="maintenance-log-detail"),

    # Fuel Logs
    path("<int:machinery_id>/fuelLogs/", FuelLogListCreateView.as_view(), name="fuel-log-list"),
    path("fuelLogs/<int:pk>/", FuelLogDetailView.as_view(), name="fuel-log-detail"),

    # Spare Parts
    path("<int:machinery_id>/spareParts/", SparePartListCreateView.as_view(), name="spare-part-list"),
    path("spareParts/<int:pk>/", SparePartDetailView.as_view(), name="spare-part-detail"),

    # Alerts
    path("<int:machinery_id>/alerts/", AlertListCreateView.as_view(), name="alert-list"),
    path("alerts/<int:pk>/", AlertDetailView.as_view(), name="alert-detail"),

    path("<int:machinery_id>/usage-logs/", MachineryUsageLogsView.as_view(), name="machinery-usage-logs"),


]

