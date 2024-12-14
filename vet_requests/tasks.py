# vet_requests/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import VetRequest
from .utils import find_next_closest_vet, send_notification

@shared_task
def check_timed_out_requests():
    timeout_minutes = 10  # Set timeout period
    timed_out_requests = VetRequest.objects.filter(
        status='pending',
        last_assigned_at__lt=timezone.now() - timedelta(minutes=timeout_minutes)
    )

    for request in timed_out_requests:
        next_vet = find_next_closest_vet(request.farmer.location_latitude, request.farmer.location_longitude, excluded_vet=request.vet)
        if next_vet:
            request.assign_to_vet(next_vet)
            send_notification(next_vet, "New Reassigned Vet Request", "A farmer needs your assistance.")
        else:
            request.status = "unassigned"
            request.save()
            send_notification(request.farmer, "Vet Unavailable", "Currently, no vets are available. Please try again later.")

