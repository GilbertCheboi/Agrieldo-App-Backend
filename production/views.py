from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Production
from .serializers import ProductionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView


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
