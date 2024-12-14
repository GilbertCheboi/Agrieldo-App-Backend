from rest_framework import generics
from .models import Drug
from .serializers import DrugSerializer

class DrugListCreateView(generics.ListCreateAPIView):
    queryset = Drug.objects.all()
    serializer_class = DrugSerializer
