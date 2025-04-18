# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
# from django.utils.timezone import now
# from .models import Animal, ProductionData
# from farms.models import Farm
# from celery import shared_task
# from utils.sms_utils import send_sms


# @shared_task
# def send_daily_milk_report_task():
#     today = now().date()
#     farms = Farm.objects.all()
    

#     for farm in farms:
#         owner_email = getattr(farm.owner, 'email', None)
#         owner_phone = getattr(farm.owner, 'phone_number', None)
#         if not owner_email:
#             continue  # Skip farms without owner email

#         animals = Animal.objects.filter(farm=farm)
#         production_records = ProductionData.objects.filter(
#             animal__in=animals,
#             date=today
#         )

#         if not production_records.exists():
#             continue  # Skip farms with no production today

#         total_milk = sum([record.milk_yield or 0 for record in production_records])

#         production_data = [
#             {
#                 'animal_name': record.animal.name,
#                 'milk_yield': record.milk_yield,
#                 'date': record.date
#             }
#             for record in production_records
#         ]

#         html_content = render_to_string('milk_report.html', {
#             'farm': farm,
#             'total_milk': total_milk,
#             'production_data': production_data,
#             'today': today.strftime('%B %d, %Y')
#         })

#         email = EmailMessage(
#             subject=f"Daily Milk Production Report - {today.strftime('%B %d, %Y')}",
#             body=html_content,
#             from_email='info@agrieldo.com',
#             to=[owner_email]
#         )
#         email.content_subtype = 'html'
#         email.send()

#         custom_message = (
#             f"Daily Milk Report - {today.strftime('%B %d, %Y')}\n"
#             f"Farm: {farm.name}\n"
#             f"Total Production: {total_milk} liters\n"
#             f"Top Producers:\n"
#         )

#         # Include details of up to 3 top-producing animals
#         top_animals = sorted(production_records, key=lambda x: x.milk_yield, reverse=True)[:3]

#         for record in top_animals:
#             custom_message += f"- {record.animal.name}: {record.milk_yield}L\n"

#         custom_message += "Keep up the great work!"

#         response = send_sms(custom_message, owner_phone)
#         print(response)  # Check the API response

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.timezone import now
from .models import Animal, ProductionData
from farms.models import Farm
from celery import shared_task
from utils.sms_utils import send_sms

@shared_task
def send_daily_milk_report_task():
    today = now().date()
    farms = Farm.objects.all()
    
    for farm in farms:
        owner_email = getattr(farm.owner, 'email', None)
        owner_phone = getattr(farm.owner, 'phone_number', None)
        
        if not owner_email and not owner_phone:
            continue  # Skip farms without contact details

        animals = Animal.objects.filter(farm=farm)
        production_records = ProductionData.objects.filter(
            animal__in=animals,
            date=today
        )

        if not production_records.exists():
            continue  # Skip farms with no production today

        total_milk = sum(record.milk_yield or 0 for record in production_records)

        production_data = [
            {
                'animal_name': record.animal.name,
                'milk_yield': record.milk_yield,
                'date': record.date
            }
            for record in production_records
        ]

        if owner_email:
            html_content = render_to_string('milk_report.html', {
                'farm': farm,
                'total_milk': total_milk,
                'production_data': production_data,
                'today': today.strftime('%B %d, %Y')
            })

            email = EmailMessage(
                subject=f"Daily Milk Production Report - {today.strftime('%B %d, %Y')}",
                body=html_content,
                from_email='info@agrieldo.com',
                to=[owner_email]
            )
            email.content_subtype = 'html'
            email.send()

        if owner_phone:
            custom_message = (
                f"Daily Milk Report - {today.strftime('%B %d, %Y')}\n"
                f"Farm: {farm.name}\n"
                f"Total Production: {total_milk} liters\n"
                f"Top Producers:\n"
            )

            # Include details of up to 3 top-producing animals
            top_animals = sorted(production_records, key=lambda x: x.milk_yield, reverse=True)[:3]

            for record in top_animals:
                custom_message += f"- {record.animal.name}: {record.milk_yield}L\n"

            custom_message += "Keep up the great work!"

            response = send_sms(custom_message, owner_phone)
            print(response)  # Check the API response

@shared_task
def send_animal_alerts_task():
    today = now().date()
    farms = Farm.objects.all()

    for farm in farms:
        owner_email = getattr(farm.owner, 'email', None)
        owner_phone = getattr(farm.owner, 'phone_number', None)

        if not owner_email and not owner_phone:
            continue

        animals = Animal.objects.filter(farm=farm)
        farm_alerts = []
        sms_alerts = []  # Stores critical alerts for SMS

        for animal in animals:
            alerts = []

            # Get latest production record
            latest_record = ProductionData.objects.filter(animal=animal).order_by('-date').first()

            if latest_record:
                if latest_record.scc and latest_record.scc > 200:
                    alerts.append("High SCC Detected")

                if latest_record.milk_yield and latest_record.milk_yield < 10:
                    alerts.append("Low Milk Production (< 10L)")

                recent_records = ProductionData.objects.filter(animal=animal).order_by('-date')[:2]
                if recent_records.count() == 2:
                    latest = recent_records[0].milk_yield
                    previous = recent_records[1].milk_yield
                    if latest < previous - 1:
                        alerts.append(f"Milk Production Dropping ({round(previous - latest, 1)}L)")
                        sms_alerts.append(f"{animal.name}: Milk drop ({round(previous - latest, 1)}L)")

            # Reproductive heat check
            if animal.reproductive_history.exists():
                last_repro = animal.reproductive_history.latest('date').date
                if (today - last_repro).days > 21:
                    alerts.append("Due for Heat Check")

            # Expected calving check
            if hasattr(animal, 'lactation_status') and animal.lactation_status and animal.lactation_status.expected_calving_date:
                edc = animal.lactation_status.expected_calving_date
                days_until = (edc - today).days
                if 0 < days_until <= 30:
                    alerts.append(f"Upcoming Calving in {days_until} days ({edc.strftime('%Y-%m-%d')})")

            if alerts:
                farm_alerts.append({
                    'animal_name': animal.name,
                    'alerts': alerts
                })

        if not farm_alerts:
            continue  # No alerts, no need to email

        html_content = render_to_string('animal_alerts.html', {
            'farm': farm,
            'alerts': farm_alerts,
            'today': today.strftime('%B %d, %Y')
        })

        email = EmailMessage(
            subject=f"Animal Alerts - {today.strftime('%B %d, %Y')}",
            body=html_content,
            from_email='info@agrieldo.com',
            to=[owner_email]
        )
        email.content_subtype = 'html'
        email.send()

        # Send SMS if there are critical alerts
        if sms_alerts and owner_phone:
            sms_message = f"Animal Alerts - {today.strftime('%B %d, %Y')}\nFarm: {farm.name}\n"
            sms_message += "\n".join(sms_alerts)
            sms_message += "\nCheck details in your email."

            response = send_sms(sms_message, owner_phone)
            print(response)  # Check the API response
