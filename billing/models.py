from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction



class Invoice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        null=True,
        blank=True
    )
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer_name}"

    
    def generate_pdf(self):
        """Generate the PDF version of the invoice and return it as a ContentFile."""

        # Ensure total price is precomputed for template use
        items = self.invoice_items.all()
        for item in items:

            item.total_price = item.quantity * item.unit_price  # Compute item total

        grand_total = sum(item.total_price for item in items)
        # Render HTML content for the invoice
        html_content = render_to_string('invoice_pdf.html', {'invoice': self, 'items': items, 'grand_total': grand_total})

        # Generate PDF from the rendered HTML content
        pdf_bytes = HTML(string=html_content).write_pdf()

        # Store the PDF in an in-memory file
        pdf_file = BytesIO(pdf_bytes)

        # Wrap the BytesIO stream into Django's ContentFile (for easy attachment)
        return pdf_file



    def send_invoice_email(self,  grand_total=None):
        """Send the invoice details in HTML and attach the PDF"""
        try:
            # Generate the PDF for the invoice
            pdf_file = self.generate_pdf()
            if not pdf_file:
                print(f"Error: PDF generation failed for Invoice #{self.id}")
                return

            # Calculate totals
            items = self.invoice_items.all()
            for item in items:
                item.total_price = item.quantity * item.unit_price  # Compute item total

            if grand_total is None:

                grand_total = sum(item.total_price for item in items)  # Calculate grand total if not passed


            # Create the email content (HTML)
            subject = f"Invoice #{self.id} from Agrieldo Farm Management"
            body = render_to_string('invoice_email.html', {
                'invoice': self,
                'items': items,
                'grand_total': grand_total
            })

            # Create the email message
            email = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],  # Send to the customer email
            )
            email.content_subtype = 'html'  # Set content type as HTML

            # Attach the PDF to the email
            email.attach(f"Invoice_{self.id}.pdf", pdf_file.getvalue(), 'application/pdf')

            # Send the email
            email_status = email.send()

            if email_status:
                print(f"Invoice #{self.id} email sent successfully.")
            else:
                print(f"Failed to send Invoice #{self.id} email.")

        except Exception as e:
            # Log any exceptions that occur during the email sending process
            print(f"Error sending invoice email: {e}")


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='invoice_items', on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.quantity} x Ksh.{self.unit_price}"




class Quotations(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quotations',
        null=True,
        blank=True
    )
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quotations #{self.id} - {self.customer_name}"


    def generate_quotation_pdf(self):
        """Generate the PDF version of the invoice and return it as a ContentFile."""

        # Ensure total price is precomputed for template use
        items = self.quotation_items.all()
        for item in items:

            item.total_price = item.quantity * item.unit_price  # Compute item total

        grand_total = sum(item.total_price for item in items)
        # Render HTML content for the invoice
        html_content = render_to_string('quotation_pdf.html', {'quotation': self, 'items': items, 'grand_total': grand_total})

        # Generate PDF from the rendered HTML content
        pdf_bytes = HTML(string=html_content).write_pdf()

        # Store the PDF in an in-memory file
        pdf_file = BytesIO(pdf_bytes)

        # Wrap the BytesIO stream into Django's ContentFile (for easy attachment)
        return pdf_file


    def send_quotation_email(self,  grand_total=None):
        """Send the invoice details in HTML and attach the PDF"""
        try:
            # Generate the PDF for the invoice
            pdf_file = self.generate_quotation_pdf()
            if not pdf_file:
                print(f"Error: PDF generation failed for Quotation #{self.id}")
                return

            # Calculate totals
            items = self.quotation_items.all()
            for item in items:
                item.total_price = item.quantity * item.unit_price  # Compute item total

            if grand_total is None:

                grand_total = sum(item.total_price for item in items)  # Calculate grand total if not passed


            # Create the email content (HTML)
            subject = f"Quotations #{self.id} from Agrieldo Farm Management"
            body = render_to_string('quotation_email.html', {
                'quotation': self,
                'items': items,
                'grand_total': grand_total
            })

            # Create the email message
            email = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],  # Send to the customer email
            )
            email.content_subtype = 'html'  # Set content type as HTML

            # Attach the PDF to the email
            email.attach(f"Quotations_{self.id}.pdf", pdf_file.getvalue(), 'application/pdf')

            # Send the email
            email_status = email.send()
            if email_status:
                print(f"Quotations #{self.id} email sent successfully.")
            else:
                print(f"Failed to send Quotation #{self.id} email.")

        except Exception as e:
            # Log any exceptions that occur during the email sending process
            print(f"Error sending Quotation email: {e}")

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotations, related_name='quotation_items', on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.quantity} x Ksh.{self.unit_price}"



class Receipt(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    payment_date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque')
    ])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for {self.customer_name}"

    def generate_pdf(self):
        """Generate the PDF version of the receipt and return it as a ContentFile."""
        items = self.receipt_items.all()
        total_amount = sum(item.total_price() for item in items)
        html_content = render_to_string('receipt_pdf.html', {'receipt': self, 'items': items, 'total_amount': total_amount})
        pdf_bytes = HTML(string=html_content).write_pdf()
        pdf_file = BytesIO(pdf_bytes)
        return pdf_file

    def send_receipt_email(self):
        """Send the receipt details via email with a PDF attachment."""
        try:
            pdf_file = self.generate_pdf()
            subject = f"Receipt for Payment"
            items = self.receipt_items.all()
            total_amount = sum(item.total_price() for item in items)
            body = render_to_string('receipt_email.html', {'receipt': self, 'items': items, 'total_amount': total_amount})
            email = EmailMessage(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [self.customer_email],
            )
            email.content_subtype = 'html'
            email.attach(f"Receipt_{self.id}.pdf", pdf_file.getvalue(), 'application/pdf')
            email.send()
            print(f"Receipt email sent to {self.customer_email}")
        except Exception as e:
            print(f"Error sending receipt email: {e}")

class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, related_name='receipt_items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"
