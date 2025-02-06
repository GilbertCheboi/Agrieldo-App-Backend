from django.urls import path
from .views import InvoiceListCreateView
from .views import InvoiceDetailView, QuotationListCreateView, QuotationDetailView

urlpatterns = [
    path("invoices/", InvoiceListCreateView.as_view(), name="invoice-list"),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path("quotations/", QuotationListCreateView.as_view(), name="quotation-list"),
    path('quotations/<int:pk>/', QuotationDetailView.as_view(), name='quotation-detail'),


]

