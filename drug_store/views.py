from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

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

    def create(self, request, *args, **kwargs):
        print("\n===== 🔥 RAW DRUG ORDER REQUEST DATA =====")
        print(request.data)

        serializer = self.get_serializer(data=request.data)
        is_valid = serializer.is_valid(raise_exception=False)

        # ALWAYS print validation errors
        if serializer.errors:
            print("\n===== ❌ DRUG ORDER VALIDATION ERRORS =====")
            print(serializer.errors)
            print("==========================================\n")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If valid: save and print success
        instance = serializer.save()

        print("\n===== ✅ DRUG ORDER CREATED SUCCESSFULLY =====")
        print(serializer.data)
        print("==============================================\n")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

