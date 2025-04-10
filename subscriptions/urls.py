from django.urls import path
from .views import SubscriptionListCreateView, LatestSubscriptionView, PackageListView

urlpatterns = [
    path('', LatestSubscriptionView.as_view(), name='subscription-list-view'),
    path('add/', SubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('packages/', PackageListView.as_view(), name='package-list'),

]
