from rest_framework import generics
from .models import Category, FeedProduct, Order
from .serializers import CategorySerializer, FeedProductSerializer, OrderSerializer

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductListView(generics.ListCreateAPIView):
    serializer_class = FeedProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return FeedProduct.objects.filter(category_id=category_id)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeedProduct.objects.all()
    serializer_class = FeedProductSerializer

class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
