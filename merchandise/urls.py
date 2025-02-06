# merchandise/urls.py

from django.urls import path
from .views import MerchandiseListView

urlpatterns = [
    path('merchandise/', MerchandiseListView.as_view(), name='merchandise-list'),
]

