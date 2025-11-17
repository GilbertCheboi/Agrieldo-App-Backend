from django.urls import path
from .views import (
    CreateListingView,
    MarketListingListView,
    MarketListingDetailView,
    ToggleListingStatusView
)

urlpatterns = [
    # POST should come here
    path('listings/', CreateListingView.as_view(), name='create-listing'),

    # GET list
    path('listings/all/', MarketListingListView.as_view(), name='market-listings'),

    # GET detail
    path('listings/<int:pk>/', MarketListingDetailView.as_view(), name='listing-detail'),

    # PATCH toggle status
    path('listings/<int:pk>/toggle/', ToggleListingStatusView.as_view(), name='toggle-listing'),
]

