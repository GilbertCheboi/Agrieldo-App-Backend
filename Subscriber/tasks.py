from celery import shared_task
from django.template.loader import render_to_string
from .models import Subscriber, Newsletter
from .utils import send_html_newsletter

@shared_task
def send_weekly_html_newsletter_task():
    """
    Fetches the latest unsent newsletter and sends it to all active subscribers.
    """
    from django.utils.timezone import now
    print(f"Task started at {now()}")

    try:
        newsletter = Newsletter.objects.filter(is_sent=False).latest('send_date')
        print(f"Found newsletter: {newsletter.subject}")
    except Newsletter.DoesNotExist:
        print("No unsent newsletter found.")
        return

    subject = newsletter.subject
    html_content = newsletter.html_content
    recipient_list = Subscriber.objects.filter(is_active=True).values_list('email', flat=True)

    # Send newsletter
    send_html_newsletter(subject, html_content, recipient_list)

    # Mark the newsletter as sent
    newsletter.is_sent = True
    newsletter.save()
    print(f"Newsletter '{subject}' sent to {len(recipient_list)} recipients.")

