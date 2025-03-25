import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from utils.sms_utils import send_sms

from .models import HealthRecord, ReproductiveHistory
from farms.models import FarmVet  # Use FarmVet model to get assigned vets

logger = logging.getLogger(__name__)

@receiver(post_save, sender=HealthRecord)
def send_health_record_email(sender, instance, created, **kwargs):
    if created:
        owner_email = instance.animal.owner.email
        farm_vet = FarmVet.objects.filter(farm=instance.animal.farm).first()
        vet_email = farm_vet.user.email if farm_vet else None
        owner_phone = instance.animal.owner.phone_number
        vet_phone = farm_vet.user.phone_number if farm_vet else None

        logger.info(f"Signal triggered for HealthRecord: {instance.animal.tag}, sending to Owner: {owner_email} and Vet: {vet_email or 'N/A'}")

        try:
            subject = f"New Health Record for {instance.animal.tag}"
            context = {
                'animal_tag': instance.animal.tag,
                'animal_name': instance.animal.name,
                'date': instance.date,
                'type': instance.type,
                'details': instance.details,
                'is_sick': instance.is_sick,
                'clinical_signs': instance.clinical_signs,
                'diagnosis': instance.diagnosis,
                'treatment': instance.treatment,
                'cost': instance.cost,
            }

            # Email to Owner
            html_message_owner = render_to_string('health_record_email.html', context)
            message_owner = (
                f"A new health record has been created:\n"
                f"Animal: {instance.animal.tag} ({instance.animal.name or 'Unnamed'})\n"
                f"Date: {instance.date}\n"
                f"Type: {instance.type}\n"
                f"Details: {instance.details}\n"
                f"Sick: {'Yes' if instance.is_sick else 'No'}\n"
                f"Clinical Signs: {instance.clinical_signs or 'N/A'}\n"
                f"Diagnosis: {instance.diagnosis or 'N/A'}\n"
                f"Treatment: {instance.treatment or 'N/A'}\n"
                f"Cost: {instance.cost or 'N/A'}"

            )
            # Build the record text: always include the tag, and add the name in parentheses if available
            record_for_text = f"a new health record for {instance.animal.tag}"
            cost = f"({instance.cost})"
            if instance.animal.name:
                record_for_text += f" ({instance.animal.name})"
            custom_message = f"Greetings, {record_for_text} has been added.\n Cost Ksh. {cost}\n Please login to your dashboard to check.\n\n"

            send_mail(subject, message_owner, settings.DEFAULT_FROM_EMAIL, [owner_email], html_message=html_message_owner)
            response = send_sms(custom_message, owner_phone)
            print(response)  # Check the API response

            # Email to Vet
            if vet_email:
                html_message_vet = render_to_string('health_record_email_vet.html', context)
                send_mail(subject, message_owner, settings.DEFAULT_FROM_EMAIL, [vet_email], html_message=html_message_vet)
                send_mail(subject, message_owner, settings.DEFAULT_FROM_EMAIL, [owner_email], html_message=html_message_owner)
                response = send_sms(custom_message, vet_phone)
            logger.info("Health record emails sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send health record email: {type(e).__name__} - {str(e)}", exc_info=True)


@receiver(post_save, sender=ReproductiveHistory)
def send_reproductive_record_email(sender, instance, created, **kwargs):
    if created:
        owner_email = instance.animal.owner.email
        farm_vet = FarmVet.objects.filter(farm=instance.animal.farm).first()
        vet_email = farm_vet.user.email if farm_vet else None
        owner_phone = instance.animal.owner.phone_number
        vet_phone = farm_vet.user.phone_number if farm_vet else None

        logger.info(f"Signal triggered for ReproductiveHistory: {instance.animal.tag}, sending to Owner: {owner_email} and Vet: {vet_email or 'N/A'}")

        try:
            subject = f"New Reproductive Record for {instance.animal.tag}"
            context = {
                'animal_tag': instance.animal.tag,
                'animal_name': instance.animal.name,
                'date': instance.date,
                'event': instance.event,
                'details': instance.details,
                'cost': instance.cost,
                'expected_calving_date': instance.expected_calving_date,
            }

            # Email to Owner
            html_message_owner = render_to_string('reproductive_record_email.html', context)
            message_owner = (
                f"A new reproductive record has been created:\n"
                f"Animal: {instance.animal.tag} ({instance.animal.name or 'Unnamed'})\n"
                f"Date: {instance.date}\n"
                f"Event: {instance.event}\n"
                f"Details: {instance.details or 'N/A'}\n"
                f"Expected Calving Date: {instance.expected_calving_date or 'N/A'}\n"
                f"Cost: {instance.cost or 'N/A'}"

            )

            # Build the record text: always include the tag, and add the name in parentheses if available
            record_for_text = f"a new reproductive health record for {instance.animal.tag}"
            cost = f"({instance.cost})"

            if instance.animal.name:
                record_for_text += f" ({instance.animal.name})"

            custom_message = f"Greetings, {record_for_text} has been added. \n Cost Ksh. {cost}\n  Please login to your dashboard to check.\n\n"

            send_mail(subject, message_owner, settings.DEFAULT_FROM_EMAIL, [owner_email], html_message=html_message_owner)
            response = send_sms(custom_message, owner_phone)
            print(response)  # Check the API response

            # Email to Vet
            if vet_email:
                html_message_vet = render_to_string('reproductive_record_email_vet.html', context)
                send_mail(subject, message_owner, settings.DEFAULT_FROM_EMAIL, [vet_email], html_message=html_message_vet)
                response = send_sms(custom_message, vet_phone)
                print(response)  # Check the API response

            logger.info("Reproductive record emails sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send reproductive record email: {type(e).__name__} - {str(e)}", exc_info=True)

