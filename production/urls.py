from django.urls import path
from .views import (ProductionList, ProductionDetail, add_production, ProductionByAnimalView, ProductionRecordListCreateView,
    ProductionRecordDetailView,
    TodayProductionView,
    ProductionHistoryView,)


urlpatterns = [
    # Endpoint to list all productions for the logged-in user, with filters for date, month, or year
    path('list_production/', ProductionList.as_view(), name='production-list'),

    # Endpoint to retrieve, update or delete a specific production record by pk
    path('update_production/<int:pk>/', ProductionDetail.as_view(), name='production-detail'),

    # Endpoint to add a new production record
    path('add_production/', add_production, name='add-production'),

    path('detail_animal/<int:animal_id>/', ProductionByAnimalView.as_view(), name='productions-by-animal'),
    path('records/', ProductionRecordListCreateView.as_view(), name='production_list_create'),
    path('records/<int:pk>/', ProductionRecordDetailView.as_view(), name='production_detail'),
    path('records/today/', TodayProductionView.as_view(), name='today_production'),
    path('records/history/', ProductionHistoryView.as_view(), name='production_history'),
]
