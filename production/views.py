from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Production, ProductionRecord
from .serializers import ProductionSerializer,  ProductionRecordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import generics, permissions
from .permissions import IsFarmerOrStaff
from django.utils.timezone import now


# View to add a new production record
@api_view(['POST'])
def add_production(request):
    if request.method == 'POST':
        # Use the authenticated user as the farmer
        serializer = ProductionSerializer(data=request.data, context={'request': request})  # Pass request context
        if serializer.is_valid():
            serializer.save()  # The 'farmer' field is automatically set in the serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Validation Errors: ", serializer.errors)  # Log the validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to get, update or delete specific production records by primary key (pk)
class ProductionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Restricts the returned productions to the logged-in user.
        """
        return self.queryset.filter(farmer=self.request.user)


# View to list productions for a specific date
class ProductionList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns production records for the logged-in user based on the given filter (date, month, or year).
        """
        # Get the logged-in user
        farmer = request.user
        
        # Get the query parameters for date, month, and year
        date = request.query_params.get('date', None)
        month = request.query_params.get('month', None)
        year = request.query_params.get('year', None)

        # Filter by date if 'date' is provided
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                productions = Production.objects.filter(farmer=farmer, date=date_obj)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by month if 'month' is provided
        elif month:
            try:
                # Check if the month is in the format YYYY-MM
                month_obj = datetime.strptime(month, '%Y-%m').date()
                productions = Production.objects.filter(farmer=farmer, date__year=month_obj.year, date__month=month_obj.month)
            except ValueError:
                return Response({"error": "Invalid month format. Use YYYY-MM."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by year if 'year' is provided
        elif year:
            try:
                # Ensure year is a valid integer
                productions = Production.objects.filter(farmer=farmer, date__year=int(year))
            except ValueError:
                return Response({"error": "Invalid year format. Use YYYY."}, status=status.HTTP_400_BAD_REQUEST)

        else:
            # If no filter is applied, return all production records for the user
            productions = Production.objects.filter(farmer=farmer)

        # Serialize and return the production data
        serializer = ProductionSerializer(productions, many=True)
        return Response(serializer.data)


class ProductionByAnimalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, animal_id):
        try:
            # Filter production records by animal ID
            productions = Production.objects.filter(animal_id=animal_id).order_by('-date')
            
            if not productions.exists():
                return Response(
                    {"message": "No production records found for this animal."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Serialize the data
            serializer = ProductionSerializer(productions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
# ✅ List and Create Production Records




class ProductionRecordListCreateView(APIView):
    """
    Handles listing and creating production records.
    Only farmers and staff can create records for their farm.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.user_type == 1:  # Farmer (Owner)
            records = ProductionRecord.objects.filter(farm__owner=user)
        elif user.user_type == 3:  # Staff
            records = ProductionRecord.objects.filter(farm__staff=user)
        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductionRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new production record.
        Staff and farmers can add records to their farm.
        """
        user = request.user
        farm = None

        if user.user_type == 1:  # Farmer (Owner)
            farm = user.owned_farms.first()
        elif user.user_type == 3:  # Staff
            farm = user.staff_farms.first()

        if not farm:
            return Response({"message": "No associated farm found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductionRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(farm=farm, farmer=user)  # ✅ Assign farmer explicitly
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductionRecordDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific production record.
    Only farm owners and staff can modify records for their farm.
    """
    permission_classes = [permissions.IsAuthenticated, IsFarmerOrStaff]

    def get_object(self, pk, user):
        try:
            record = ProductionRecord.objects.get(pk=pk)
            if record.farm.owner == user or user in record.farm.staff.all():
                return record
            return None
        except ProductionRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response({"message": "Not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductionRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response({"message": "Not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductionRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        record = self.get_object(pk, request.user)
        if not record:
            return Response({"message": "Not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        record.delete()
        return Response({"message": "Record deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class TodayProductionView(APIView):
    """
    API endpoint to fetch production records for today only.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        if user.user_type == 1:  # Farmer
            records = ProductionRecord.objects.filter(farm__owner=user, created_at=today)
        elif user.user_type == 3:  # Staff
            records = ProductionRecord.objects.filter(farm__staff=user, created_at=today)
        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductionRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductionHistoryView(APIView):
    """
    API endpoint to fetch all production records except today's.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        if user.user_type == 1:  # Farmer
            records = ProductionRecord.objects.filter(farm__owner=user).exclude(created_at=today)
        elif user.user_type == 3:  # Staff
            records = ProductionRecord.objects.filter(farm__staff=user).exclude(created_at=today)
        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductionRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

