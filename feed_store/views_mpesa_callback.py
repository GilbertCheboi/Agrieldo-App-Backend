from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from feed_store.models import FeedOrder

@api_view(['POST'])
def mpesa_callback(request):

    try:
        data = request.data
        body = data["Body"]["stkCallback"]

        result_code = body["ResultCode"]
        metadata = body["CallbackMetadata"]["Item"]

        phone = None
        mpesa_receipt = None
        amount = None

        for entry in metadata:
            if entry["Name"] == "PhoneNumber":
                phone = entry["Value"]
            if entry["Name"] == "MpesaReceiptNumber":
                mpesa_receipt = entry["Value"]
            if entry["Name"] == "Amount":
                amount = entry["Value"]

        # Extract order ID from AccountReference
        account_ref = body["MerchantRequestID"]
        order_id = account_ref.replace("Order-", "")

        # Update order
        FeedOrder.objects.filter(id=order_id).update(
            payment_status="PAID",
            mpesa_receipt=mpesa_receipt
        )

        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

