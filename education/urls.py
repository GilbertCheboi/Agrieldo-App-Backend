from django.urls import path
from .views import EducationalMaterialListCreateView

urlpatterns = [
    path('materials/', EducationalMaterialListCreateView.as_view(), name='material-list-create'),
]
