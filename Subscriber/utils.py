# utils.py
from django.core.mail import EmailMultiAlternatives

def send_html_newsletter(subject, html_content, recipient_list):
    """
    Sends HTML email newsletters to a list of recipients.
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body="This is the plain text fallback.",
        to=recipient_list,
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

