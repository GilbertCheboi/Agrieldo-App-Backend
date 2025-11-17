import requests
import base64
from datetime import datetime
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import UnifiedOrder, UnifiedOrderItem


@api_view(['POST'])
def mpesa_stk_push(request):
    """
    Initiates STK Push for a unified checkout transaction
    """
    try:
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        unified_order_id = request.data.get("unified_order")

        if not unified_order_id:
            return Response({"error": "unified_order is required"}, status=400)

        # 1. Get Access Token
        token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth = requests.get(token_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
        access_token = auth.json().get("access_token")

        # 2. Generate Password
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
        password = base64.b64encode(data_to_encode.encode()).decode("utf-8")

        # 3. STK Payload
        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": f"Unified-{unified_order_id}",
            "TransactionDesc": "Agrieldo Unified Checkout",
        }

        response = requests.post(stk_url, json=payload, headers=headers)

        # Save checkout ID for later callback matching
        res_json = response.json()
        if "CheckoutRequestID" in res_json:
            UnifiedOrder.objects.filter(id=unified_order_id).update(
                mpesa_checkout_id=res_json["CheckoutRequestID"]
            )

        return Response(res_json, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)



@api_view(['POST'])
def mpesa_callback(request):
    """
    Safaricom callback marks Unified Order + all Feed & Drug orders as PAID
    """
    try:
        data = request.data
        body = data["Body"]["stkCallback"]

        result_code = body["ResultCode"]
        checkout_id = body["CheckoutRequestID"]

        if result_code != 0:
            return Response({"status": "failed"}, status=200)

        # Extract metadata
        metadata = body["CallbackMetadata"]["Item"]
        phone = mpesa_receipt = amount = None

        for entry in metadata:
            if entry["Name"] == "PhoneNumber":
                phone = entry["Value"]
            if entry["Name"] == "MpesaReceiptNumber":
                mpesa_receipt = entry["Value"]
            if entry["Name"] == "Amount":
                amount = entry["Value"]

        # Find unified order
        try:
            u_order = UnifiedOrder.objects.get(mpesa_checkout_id=checkout_id)
        except UnifiedOrder.DoesNotExist:
            return Response({"error": "Unified order not found"}, status=404)

        # Mark unified order PAID
        u_order.is_paid = True
        u_order.save()

        # Mark individual feed/drug orders as PAID
        for item in u_order.items.all():
            if item.feed_order:
                item.feed_order.payment_status = "PAID"
                item.feed_order.mpesa_receipt = mpesa_receipt
                item.feed_order.save()

            if item.drug_order:
                item.drug_order.payment_status = "PAID"
                item.drug_order.mpesa_receipt = mpesa_receipt
                item.drug_order.save()

        return Response({"status": "success"}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=400)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from feed_store.models import FeedOrder, FeedProduct
from drug_store.models import DrugOrder, Drug
from .models import UnifiedOrder, UnifiedOrderItem


class UnifiedCheckoutView(APIView):
    def post(self, request):
        cart = request.data.get("cart", [])
        name = request.data.get("customer_name")
        phone = request.data.get("customer_contact")
        total = request.data.get("total_amount")

        if not cart:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        if not name or not phone:
            return Response({"detail": "Customer name and phone required"}, status=status.HTTP_400_BAD_REQUEST)
        if total is None:
            return Response({"detail": "Total amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create unified order record
        unified = UnifiedOrder.objects.create(
            customer_name=name,
            customer_contact=phone,
            total_amount=Decimal(total)
        )

        feed_ids = []
        drug_ids = []

        for item in cart:
            q = item.get("quantity", 1)
            item_type = item.get("type")
            item_id = item.get("id")

            if not item_type or item_id is None:
                continue

            # Extract numeric ID for both feed & drug
            try:
                numeric_id = int("".join(filter(str.isdigit, str(item_id))))
            except ValueError:
                continue

            # ========================
            # FEED ORDER CREATION
            # ========================
            if item_type == "feed":
                try:
                    product = FeedProduct.objects.get(id=numeric_id)
                except FeedProduct.DoesNotExist:
                    continue

                total_price = Decimal(product.price) * Decimal(q)

                order = FeedOrder.objects.create(
                    customer_name=name,
                    customer_contact=phone,
                    product=product,
                    quantity=q,
                    total_price=total_price,
                )

                UnifiedOrderItem.objects.create(unified_order=unified, feed_order=order)
                feed_ids.append(order.id)

            # ========================
            # DRUG ORDER CREATION
            # ========================
            elif item_type == "drug":
                try:
                    drug = Drug.objects.get(id=numeric_id)
                except Drug.DoesNotExist:
                    continue

                total_price = Decimal(drug.price) * Decimal(q)

                order = DrugOrder.objects.create(
                    customer_name=name,
                    customer_contact=phone,
                    drug=drug,
                    quantity=q,
                    total_price=total_price,
                )

                UnifiedOrderItem.objects.create(unified_order=unified, drug_order=order)
                drug_ids.append(order.id)

        return Response({
            "unified_order_id": unified.id,
            "feed_orders": feed_ids,
            "drug_orders": drug_ids,
            "total_amount": unified.total_amount
        }, status=status.HTTP_201_CREATED)

