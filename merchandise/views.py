from rest_framework import generics
from rest_framework.permissions import AllowAny  # To allow any user to access the view
from .models import Merchandise
from .serializers import MerchandiseSerializer

class MerchandiseListView(generics.ListAPIView):
    queryset = Merchandise.objects.all()
    serializer_class = MerchandiseSerializer
    permission_classes = [AllowAny]  # This line ensures the view is accessible to everyone (public access)

