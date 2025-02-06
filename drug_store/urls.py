from django.urls import path
from .views import DrugCategoryListView, DrugListView, DrugDetailView, DrugOrderListView

urlpatterns = [
    path('categories/', DrugCategoryListView.as_view(), name='drug-category-list'),
    path('categories/<int:category_id>/drugs/', DrugListView.as_view(), name='drug-list'),
    path('drugs/<int:pk>/', DrugDetailView.as_view(), name='drug-detail'),
    path('orders/', DrugOrderListView.as_view(), name='drug-order-list'),
]
