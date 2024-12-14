from django.urls import path
from .views import InvoiceListCreateView

urlpatterns = [
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list-create'),
]
