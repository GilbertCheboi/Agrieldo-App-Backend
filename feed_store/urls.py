from django.urls import path
from .views import (
    CategoryListView,
    ProductListView,
    ProductDetailView,
    OrderListView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]


from .views_mpesa import mpesa_stk_push
from .views_mpesa_callback import mpesa_callback

urlpatterns += [
    path('stk_push/', mpesa_stk_push, name='mpesa_stk_push'),
    path('mpesa_callback/', mpesa_callback, name='mpesa_callback'),
]

