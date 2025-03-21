from django.core.management.base import BaseCommand
from inventory.utils import send_produce_report_email

class Command(BaseCommand):
    help = 'Send Agrieldo Produce Report Email with PDF attachment'

    def handle(self, *args, **kwargs):
        send_produce_report_email()
        self.stdout.write(self.style.SUCCESS('Successfully sent produce report email.'))
