from django.urls import path
from .views import (
    ProduceListCreateView,
    StoreListCreateView,
    OutletListCreateView,
    InventoryListCreateView,
    TransactionListCreateView,
)

urlpatterns = [
    path('produce/', ProduceListCreateView.as_view(), name='produce-list-create'),
    path('stores/', StoreListCreateView.as_view(), name='store-list-create'),
    path('outlets/', OutletListCreateView.as_view(), name='outlet-list-create'),
    path('inventory/', InventoryListCreateView.as_view(), name='inventory-list-create'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
]

