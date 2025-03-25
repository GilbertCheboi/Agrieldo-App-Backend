
# animals/urls.py
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
    FeedManagementListCreateView
)

urlpatterns = [
    # Existing Views
    path('daily-totals/', DailyProductionTotalsView.as_view(), name='daily-production-totals'),
    path('health-records/<int:id>/', HealthRecordRetrieveUpdateView.as_view(), name='health-record-update'),
    path('', AnimalListView.as_view(), name='animal-list'),
    path('<int:pk>/', AnimalDetailView.as_view(), name='animal-detail'),

    # New Views for Adding Records
    path('production-data/', ProductionDataListCreateView.as_view(), name='production-data-list-create'),
    path('health-records/', HealthRecordListCreateView.as_view(), name='health-records-list-create'),
    path('reproductive-history/', ReproductiveHistoryListCreateView.as_view(), name='reproductive-history-list-create'),
    path('add/', AnimalListCreateView.as_view(), name='animal-list-create'),
    path('financial/', FinancialDetailsListCreateView.as_view(), name='financial_list_create'),
    path('feed-management/', FeedManagementListCreateView.as_view(), name='feed_list_create'),
]
