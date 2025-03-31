from django.urls import path
from .views import (
    DailyProductionTotalsView,
    HealthRecordRetrieveUpdateView,
    AnimalListView,
    AnimalDetailView,
    ProductionDataListCreateView,
    HealthRecordListCreateView,
    ReproductiveHistoryListCreateView,
    AnimalListCreateView,
    FinancialDetailsListCreateView,
    FeedManagementListCreateView,
    LactationPeriodListCreateView,  # Added
    MilkProductionCreateView,
    LactatingAnimalsListView,
    DailyMilkProductionSummaryView
)

urlpatterns = [
    # Existing Views
    path('daily-totals/', DailyProductionTotalsView.as_view(), name='daily-production-totals'),
    path('health-records/<int:id>/', HealthRecordRetrieveUpdateView.as_view(), name='health-record-update'),
    path('', AnimalListView.as_view(), name='animal-list'),
    path('<int:pk>/', AnimalDetailView.as_view(), name='animal-detail'),
    path('production-data/', ProductionDataListCreateView.as_view(), name='production-data-list-create'),
    path('health-records/', HealthRecordListCreateView.as_view(), name='health-records-list-create'),
    path('reproductive-history/', ReproductiveHistoryListCreateView.as_view(), name='reproductive-history-list-create'),
    path('add/', AnimalListCreateView.as_view(), name='animal-list-create'),
    path('financial/', FinancialDetailsListCreateView.as_view(), name='financial_list_create'),
    path('feed-management/', FeedManagementListCreateView.as_view(), name='feed_list_create'),
    path('lactation/<int:animal_id>/', LactationPeriodListCreateView.as_view(), name='lactation-list-create'),  # Must be here    
    # Lactation Period View
    path('production/milk/', ProductionDataListCreateView.as_view(), name='milk-production'),
    path('production/milk/lactating-animals/', LactatingAnimalsListView.as_view(), name='lactating-animals'),
    path('production/daily-summary/', DailyMilkProductionSummaryView.as_view(), name='daily-production-summary'),

]
