from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Produce, Store, Outlet, Inventory, Transaction
from .serializers import (
    ProduceSerializer,
    StoreSerializer,
    OutletSerializer,
    InventorySerializer,
    TransactionSerializer,
)
from django.db import transaction
from django.utils.dateparse import parse_date


class ProduceListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Return only the produce items owned by the current user
        queryset = Produce.objects.filter(user=request.user)
        serializer = ProduceSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProduceSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically set the user as the owner of the produce
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StoreListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Store.objects.all()
        serializer = StoreSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OutletListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Only return outlets for the logged-in user
        queryset = Outlet.objects.filter(user=request.user)
        serializer = OutletSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OutletSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically assign the outlet to the current user
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        inventories = Inventory.objects.filter(user=request.user)

        # Optional Date Filtering (start_date, end_date)
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            start_date = parse_date(start_date)
            inventories = inventories.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            inventories = inventories.filter(created_at__date__lte=end_date)

        serializer = InventorySerializer(inventories, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id

        try:
            with transaction.atomic():
                produce_id = data.get('produce')
                store_id = data.get('store')
                outlet_id = data.get('outlet')
                quantity = float(data.get('quantity'))

                # Transfer from store to outlet
                if store_id and outlet_id:
                    # 1. Get store inventory (store only, no outlet)
                    store_inventory = Inventory.objects.filter(
                        produce=produce_id,
                        store=store_id,
                        outlet=None,
                        user=request.user
                    ).first()

                    if not store_inventory or store_inventory.quantity < quantity:
                        return Response({"detail": "Insufficient stock in store."}, status=400)

                    # 2. Deduct from store
                    store_inventory.quantity -= quantity
                    store_inventory.save()

                    # 3. Add to outlet inventory (create or update)
                    outlet_inventory, created = Inventory.objects.get_or_create(
                        produce_id=produce_id,
                        store_id=store_id,
                        outlet_id=outlet_id,
                        user=request.user
                    )
                    outlet_inventory.quantity += quantity
                    outlet_inventory.save()

                    return Response(
                        {"detail": "Stock transferred successfully."},
                        status=status.HTTP_201_CREATED
                    )

                # If it's just an addition to store
                elif store_id and not outlet_id:
                    # Check if an inventory entry already exists (store-only)
                    store_inventory, created = Inventory.objects.get_or_create(
                        produce_id=produce_id,
                        store_id=store_id,
                        outlet=None,
                        user=request.user
                    )
                    store_inventory.quantity += quantity
                    store_inventory.save()

                    serializer = InventorySerializer(store_inventory)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

                else:
                    return Response({"detail": "Invalid input. Store is required."}, status=400)

        except Exception as e:
            return Response({"detail": str(e)}, status=500)

class TransactionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

