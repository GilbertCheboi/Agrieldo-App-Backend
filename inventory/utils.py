from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings

def send_produce_report_email():
    try:
        # STEP 1: Prepare context data
        context = {
            "report_date": "March 2025",
            "sections": [
                {
                    "title": "Tomatoes - 09/03/25",
                    "headers": ["Source", "Quantity"],
                    "rows": [
                        ["Total Received", "2 crates (50kg)"],
                        ["Kipkorgort", "0.5 crate (12kg)"],
                        ["Chep", "0.5 crate (12kg)"],
                        ["Mountain View", "3 Goros (6kg)"],
                        ["Munyaka B", "3 Goros (6kg)"],
                        ["Kapsoya", "6 Goros (12kg)"],
                    ]
                },
                {
                    "title": "Pawpaw - March 7",
                    "headers": ["Location", "Qty (pcs)"],
                    "rows": [
                        ["Kipkorgort", "12"],
                        ["Chep", "17"],
                        ["Mountain View", "2"],
                        ["Kapsoya", "4"],
                        ["Munyaka A", "2"],
                        ["Munyaka B", "4"],
                        ["Domestic (overripe)", "11"]
                    ]
                },
                {
                    "title": "Chepkoilel - March 7",
                    "headers": ["Product", "Qty"],
                    "rows": [
                        ["Tomato Passion", "120"],
                        ["Passion Fruit", "130"],
                    ]
                },
                {
                    "title": "Kipkorgot - March 7",
                    "headers": ["Product", "Qty"],
                    "rows": [
                        ["Tomato Passion", "120"],
                        ["Passion Fruit", "130"],
                    ]
                },
                {
                    "title": "Domestic - March 7",
                    "headers": ["Product", "Qty"],
                    "rows": [
                        ["Passion Fruit", "96"],
                        ["Tomato Passion", "78"],
                    ]
                },
                {
                    "title": "March 16 Summary",
                    "headers": ["Location", "Onions", "Pawpaw", "Tomatoes", "Tomato Passion", "Passion Fruit"],
                    "rows": [
                        ["Kipkorgot", "23.35kg", "18.7kg", "42.3kg", "6.9kg", "15kg"],
                        ["Mountain View", "11.7kg", "11.35kg", "4.5kg", "-", "-"],
                        ["Kapsoya", "11.7kg", "5.9kg", "4kg", "-", "-"],
                        ["Munyaka B", "11.7kg", "10.9kg", "25.3kg", "-", "-"],
                        ["Chepkoil", "36.55kg", "28.55kg", "62kg", "12.1kg", "15.1kg"],
                    ]
                }
            ]
        }

        # STEP 2: Render HTML
        html_content = render_to_string('agrieldo_email.html', context)

        # STEP 3: Create Email
        subject = f"Agrieldo Produce Report - {context['report_date']}"
        text_content = "Please see the attached produce report for Agrieldo."

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["philket@gmail.com"]
        )
        email.attach_alternative(html_content, "text/html")

        # STEP 4: Generate PDF
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        if not pisa_status.err:
            pdf_file.seek(0)
            email.attach("Agrieldo_Produce_Report.pdf", pdf_file.read(), "application/pdf")

        # STEP 5: Send Email
        email.send()
        print("Produce report email sent successfully.")

    except Exception as e:
        print(f"Error sending produce report email: {str(e)}")
