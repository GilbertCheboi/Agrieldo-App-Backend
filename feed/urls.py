from django.urls import path
from . import views

urlpatterns = [
    # Store management
    path('stores/', views.StoreListCreateView.as_view(), name='store-list-create'),

    # Feed management
    path('feeds/', views.FeedListCreateView.as_view(), name='feed-list-create'),

    # Feeding plan management
    path('feeding-plans/', views.FeedingPlanListCreateView.as_view(), name='feeding-plan-list-create'),

    # Feed animals
    path('feed-animals/', views.FeedAnimalsView.as_view(), name='feed-animals'),
]

