import requests
import base64
from datetime import datetime
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def mpesa_stk_push(request):
    try:
        phone = request.data.get("phone")
        amount = request.data.get("amount")
        order_id = request.data.get("order_id")

        # 1. Access Token
        token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth = requests.get(token_url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
        access_token = auth.json().get("access_token")

        # 2. Password
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
        password = base64.b64encode(data_to_encode.encode()).decode("utf-8")

        # 3. STK Push request
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
            "AccountReference": f"Order-{order_id}",
            "TransactionDesc": "Agrieldo Feed Purchase",
        }

        response = requests.post(stk_url, json=payload, headers=headers)
        return Response(response.json(), status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

