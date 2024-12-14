
from rest_framework import generics
from .models import EducationalMaterial
from .serializers import EducationalMaterialSerializer

class EducationalMaterialListCreateView(generics.ListCreateAPIView):
    queryset = EducationalMaterial.objects.all()
    serializer_class = EducationalMaterialSerializer
