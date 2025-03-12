from django.contrib import admin
from .models import Invoice, InvoiceItem, Quotations, QuotationItem, Receipt, ReceiptItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Number of empty forms to show by default

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'customer_phone', 'due_date', 'total_amount', 'created_at', 'updated_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_filter = ('created_at', 'due_date')
    inlines = [InvoiceItemInline]  # Display Invoice Items inline within the Invoice form

    def save_model(self, request, obj, form, change):
        # Optionally, you can modify the `save` method for custom actions before saving
        super().save_model(request, obj, form, change)

class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price')
    search_fields = ('description',)


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1  # Number of empty forms to show by default

class QuotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'customer_phone', 'due_date', 'total_amount', 'created_at', 'updated_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_filter = ('created_at', 'due_date')
    inlines = [QuotationItemInline]  # Display Invoice Items inline within the Invoice form

    def save_model(self, request, obj, form, change):
        # Optionally, you can modify the `save` method for custom actions before saving
        super().save_model(request, obj, form, change)

class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ('quotation', 'description', 'quantity', 'unit_price')
    search_fields = ('description',)


class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 1

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'payment_date', 'payment_method', 'amount_paid', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    list_filter = ('payment_method', 'payment_date')
    inlines = [ReceiptItemInline]

# Register the models in the admin interface
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem, InvoiceItemAdmin)
admin.site.register(Quotations, QuotationAdmin)
admin.site.register(QuotationItem, QuotationItemAdmin)

admin.site.register(ReceiptItem)
