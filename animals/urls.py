# urls.py

from django.urls import path
from .views import (
    AnimalListCreateView,
    AnimalDetailView,
    DairyCowListCreateView,
    DairyCowDetailView,
    BeefCowListCreateView,
    BeefCowDetailView,
    SheepListCreateView,
    SheepDetailView,
    GoatListCreateView,
    GoatDetailView,
    DairyMedicalRecordListCreateView,
    BeefMedicalRecordListCreateView,
    SheepMedicalRecordListCreateView,
    GoatMedicalRecordListCreateView,

)

urlpatterns = [
    path('animals/', AnimalListCreateView.as_view(), name='animal-list-create'),
    path('animals/<int:pk>/', AnimalDetailView.as_view(), name='animal-detail'),
    
    path('dairy-cows/', DairyCowListCreateView.as_view(), name='dairy-cow-list-create'),
    path('dairy-cows/<int:pk>/', DairyCowDetailView.as_view(), name='dairy-cow-detail'),
    path('dairy-cows/<int:pk>/medical-records/', DairyMedicalRecordListCreateView.as_view(), name='dairy_medical-record-list-create'),
    
    path('beef-cows/', BeefCowListCreateView.as_view(), name='beef-cow-list-create'),
    path('beef-cows/<int:pk>/', BeefCowDetailView.as_view(), name='beef-cow-detail'),
    path('sheep/<int:pk>/medical-records/', BeefMedicalRecordListCreateView.as_view(), name='beef_medical-record-list-create'),
    
    path('sheep/', SheepListCreateView.as_view(), name='sheep-list-create'),
    path('sheep/<int:pk>/', SheepDetailView.as_view(), name='sheep-detail'),
    path('sheep/<int:pk>/medical-records/', SheepMedicalRecordListCreateView.as_view(), name='sheep_medical-record-list-create'),
    
    path('goats/', GoatListCreateView.as_view(), name='goat-list-create'),
    path('goats/<int:pk>/', GoatDetailView.as_view(), name='goat-detail'),
    path('goats/<int:pk>/medical-records/', GoatMedicalRecordListCreateView.as_view(), name='goats_medical-record-list-create'),


]

