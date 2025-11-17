from django.urls import path
from .views import (
    UnifiedCheckoutView,
    mpesa_stk_push,
    mpesa_callback
)

urlpatterns = [
    path("checkout/unified/", UnifiedCheckoutView.as_view(), name="unified-checkout"),
    path("mpesa/checkout/", mpesa_stk_push, name="mpesa-stk-push"),
    path("mpesa/callback/", mpesa_callback, name="mpesa-callback"),
]

