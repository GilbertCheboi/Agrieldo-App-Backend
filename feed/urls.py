from django.urls import path
from .views import FeedRecordView, FarmerFeedListView

urlpatterns = [
    path('feeds/', FarmerFeedListView.as_view(), name='feed-list'),
    path('feeds/update/', FeedRecordView.as_view(), name='feed-update'),
]
