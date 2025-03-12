from django.urls import path
from .views import InvoiceListCreateView
from .views import InvoiceDetailView, QuotationListCreateView, QuotationDetailView, ReceiptListCreateView, ReceiptDetailView

urlpatterns = [
    path("invoices/", InvoiceListCreateView.as_view(), name="invoice-list"),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path("quotations/", QuotationListCreateView.as_view(), name="quotation-list"),
    path('quotations/<int:pk>/', QuotationDetailView.as_view(), name='quotation-detail'),
    path("receipts/", ReceiptListCreateView.as_view(), name="receipt-list"),
    path("receipts/<int:pk>/", ReceiptDetailView.as_view(), name="receipt-detail"),


]

