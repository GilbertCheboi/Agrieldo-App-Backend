from django.urls import path
from .views import (
    FeedListCreateAPIView,
    FeedDetailAPIView,
    FeedTransactionListCreateAPIView,
    DailyFeedConsumptionAPIView
)

urlpatterns = [
    path('feeds/', FeedListCreateAPIView.as_view(), name='feed-list-create'),
    path('feeds/<int:pk>/', FeedDetailAPIView.as_view(), name='feed-detail'),
    path('feed-transactions/', FeedTransactionListCreateAPIView.as_view(), name='feed-transaction-list-create'),
    path('feed-transactions/daily-consumption/', DailyFeedConsumptionAPIView.as_view(), name='daily-feed-consumption'),
]

