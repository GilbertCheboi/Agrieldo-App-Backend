# File: farms/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmViewSet

router = DefaultRouter()
router.register(r'farms', FarmViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
