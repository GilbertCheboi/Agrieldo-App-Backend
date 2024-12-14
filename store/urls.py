from django.urls import path
from .views import DrugListCreateView

urlpatterns = [
    path('drugs/', DrugListCreateView.as_view(), name='drug-list-create'),
]
