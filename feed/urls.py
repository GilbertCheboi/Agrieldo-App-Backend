from django.urls import path
from . import views

urlpatterns = [
    path('feeds/', views.FeedListCreateView.as_view(), name='feed-list-create'),
    path('feed-animals/', views.FeedAnimalsView.as_view(), name='feed-animals'),
    path('feeding-plans/', views.FeedingPlanListCreateView.as_view(), name='feeding-plan-list-create'),
]
