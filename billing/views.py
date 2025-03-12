from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import Invoice, Quotations, Receipt
from .serializers import InvoiceSerializer, QuotationSerializer, ReceiptSerializer

class InvoiceListCreateView(generics.ListCreateAPIView):
    queryset = Invoice.objects.prefetch_related('invoice_items')  # Fetch related items
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

class InvoiceDetailView(generics.RetrieveAPIView):
    queryset = Invoice.objects.prefetch_related('invoice_items')  # Fetch related items
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]


class QuotationListCreateView(generics.ListCreateAPIView):
    queryset = Quotations.objects.prefetch_related('quotation_items')  # Fetch related items
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]

class QuotationDetailView(generics.RetrieveAPIView):
    queryset = Quotations.objects.prefetch_related('quotation_items')  # Fetch related items
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated]
class ReceiptListCreateView(generics.ListCreateAPIView):
    queryset = Receipt.objects.prefetch_related('receipt_items')  # Fetch related items
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]

class ReceiptDetailView(generics.RetrieveAPIView):
    queryset = Receipt.objects.prefetch_related('receipt_items')  # Fetch related items
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
