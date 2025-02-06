from django.urls import path
from .views import create_auction, AuctionListView, remove_auction

urlpatterns = [
    # Endpoint for creating an auction for a specific animal
    path('create_auction/<int:animal_id>/', create_auction, name='create_auction'),

    # Endpoint for listing active auctions
    path('auctions/', AuctionListView.as_view(), name='auction_list'),

    # Endpoint for removing an auction by ID
    path('remove_auction/<int:pk>/', remove_auction, name='remove_auction'),
]

