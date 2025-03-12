from rest_framework import serializers
from .models import Invoice, InvoiceItem, Quotations, QuotationItem, Receipt, ReceiptItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, source='invoice_items', required=False)  # Make sure source is correctly set
    total_amount = serializers.SerializerMethodField()  # Compute total amount dynamically

    class Meta:
        model = Invoice
        fields = ['id', 'user', 'customer_name', 'customer_email', 'customer_phone', 'due_date', 'total_amount', 'items']

    def get_total_amount(self, obj):
        """Calculate total amount by summing up item prices."""
        return sum(item.quantity * item.unit_price for item in obj.invoice_items.all())

    def create(self, validated_data):
        items_data = validated_data.pop('invoice_items', [])  # Fetch items correctly
        invoice = Invoice.objects.create(**validated_data)

        # Create associated InvoiceItem instances
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('invoice_items', [])

        # Update Invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear existing items and recreate them
        instance.invoice_items.all().delete()
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=instance, **item_data)

        return instance



class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['id', 'description', 'quantity', 'unit_price']

class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, source='quotation_items', required=False)  # Make sure source is correctly set
    total_amount = serializers.SerializerMethodField()  # Compute total amount dynamically
    
    class Meta:
        model = Quotations
        fields = ['id', 'user', 'customer_name', 'customer_email', 'customer_phone', 'due_date', 'total_amount', 'items']

    def get_total_amount(self, obj):
        """Calculate total amount by summing up item prices."""
        return sum(item.quantity * item.unit_price for item in obj.quotation_items.all())

    def create(self, validated_data):
        items_data = validated_data.pop('quotation_items', [])  # Fetch items correctly
        quotation = Quotations.objects.create(**validated_data)

        # Create associated InvoiceItem instances
        for item_data in items_data:
            QuotationItem.objects.create(quotation=quotation, **item_data)

        return quotation

    def update(self, instance, validated_data):
        items_data = validated_data.pop('quotation_items', [])

        # Update Invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear existing items and recreate them
        instance.quotation_items.all().delete()
        for item_data in items_data:
            QuotationItem.objects.create(invoice=instance, **item_data)

        return instance

class ReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptItem
        fields = ['id', 'description', 'quantity', 'unit_price']

class ReceiptSerializer(serializers.ModelSerializer):
    items = ReceiptItemSerializer(many=True, source='receipt_items', required=False)
    amount_paid = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = ['id', 'customer_name', 'customer_email', 'customer_phone', 'payment_date', 
                  'payment_method', 'amount_paid', 'created_at', 'items']

    def get_amount_paid(self, obj):
        """Calculate total amount paid by summing up item prices."""
        return sum(item.quantity * item.unit_price for item in obj.receipt_items.all())

    def create(self, validated_data):
        items_data = validated_data.pop('receipt_items', [])
        receipt = Receipt.objects.create(**validated_data)

        # Create associated ReceiptItem instances
        for item_data in items_data:
            ReceiptItem.objects.create(receipt=receipt, **item_data)

        return receipt

    def update(self, instance, validated_data):
        items_data = validated_data.pop('receipt_items', [])

        # Update Receipt fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Clear existing items and recreate them
        instance.receipt_items.all().delete()
        for item_data in items_data:
            ReceiptItem.objects.create(receipt=instance, **item_data)

        return instance

