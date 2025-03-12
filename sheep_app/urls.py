# sheep_app/urls.py
from django.urls import path
from .views import (
    SheepListCreateView, SheepDetailView,
    SheepHealthRecordListCreateView, SheepHealthRecordDetailView,
    SheepReproductionListCreateView, SheepReproductionDetailView,
    SheepProductionListCreateView, SheepProductionDetailView,
    SheepImageListCreateView, SheepImageDetailView,
    SheepTypeListCreateView, SheepTypeDetailView
)

urlpatterns = [
    # Sheep
    path('sheep/', SheepListCreateView.as_view(), name='sheep-list-create'),
    path('sheep/<int:pk>/', SheepDetailView.as_view(), name='sheep-detail'),

    # Sheep Health Records
    path('sheep-health-records/', SheepHealthRecordListCreateView.as_view(), name='sheep-health-list-create'),
    path('sheep-health-records/<int:pk>/', SheepHealthRecordDetailView.as_view(), name='sheep-health-detail'),

    # Sheep Reproduction
    path('sheep-reproduction/', SheepReproductionListCreateView.as_view(), name='sheep-reproduction-list-create'),
    path('sheep-reproduction/<int:pk>/', SheepReproductionDetailView.as_view(), name='sheep-reproduction-detail'),

    # Sheep Production
    path('sheep-production/', SheepProductionListCreateView.as_view(), name='sheep-production-list-create'),
    path('sheep-production/<int:pk>/', SheepProductionDetailView.as_view(), name='sheep-production-detail'),

    # Sheep Images
    path('sheep-images/', SheepImageListCreateView.as_view(), name='sheep-image-list-create'),
    path('sheep-images/<int:pk>/', SheepImageDetailView.as_view(), name='sheep-image-detail'),

    # Sheep Types
    path('sheep-types/', SheepTypeListCreateView.as_view(), name='sheep-type-list-create'),
    path('sheep-types/<int:pk>/', SheepTypeDetailView.as_view(), name='sheep-type-detail'),
]
