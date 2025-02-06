from rest_framework import generics
from .models import DrugCategory, Drug, DrugOrder
from .serializers import DrugCategorySerializer, DrugSerializer, DrugOrderSerializer

class DrugCategoryListView(generics.ListCreateAPIView):
    queryset = DrugCategory.objects.all()
    serializer_class = DrugCategorySerializer

class DrugListView(generics.ListCreateAPIView):
    serializer_class = DrugSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Drug.objects.filter(category_id=category_id)

class DrugDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Drug.objects.all()
    serializer_class = DrugSerializer

class DrugOrderListView(generics.ListCreateAPIView):
    queryset = DrugOrder.objects.all()
    serializer_class = DrugOrderSerializer
