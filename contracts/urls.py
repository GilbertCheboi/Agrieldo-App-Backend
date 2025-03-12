from django.urls import path
from .views import ContractListCreateView, ContractDetailView

urlpatterns = [
    path("", ContractListCreateView.as_view(), name="contract-list-create"),
    path("<int:pk>/", ContractDetailView.as_view(), name="contract-detail"),
]

