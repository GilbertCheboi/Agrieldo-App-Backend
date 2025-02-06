# vet_requests/utils.py
from accounts.models import User

from profiles.models import Vet, Farmer
import math
from django.core.exceptions import ObjectDoesNotExist
from fcm_django.models import FCMDevice

def find_closest_vet(lat, lon, excluded_vets=[]):
    available_vets = Vet.objects.exclude(id__in=[vet.id for vet in excluded_vets])
    closest_vet = None
    min_distance = float('inf')

    for vet in available_vets:
        distance = math.sqrt((vet.location_latitude - lat)**2 + (vet.location_longitude - lon)**2)
        if distance < min_distance:
            min_distance = distance
            closest_vet = vet

    return closest_vet

def find_next_closest_vet(lat, lon, excluded_vet):
    excluded_vets = [excluded_vet] if excluded_vet else []
    return find_closest_vet(lat, lon, excluded_vets)


def send_notification(user, title, body):
    # Access the fcm_token from the User model
    if isinstance(user, Vet):
        fcm_token = user.user.fcm_token  # Access the token through the User
    elif isinstance(user, Farmer):
        fcm_token = user.user.fcm_token  # Access the token through the User
    else:
        return  # Return if user is neither a Vet nor a Farmer

    if fcm_token:  # Ensure there is a valid fcm_token
        # Create or get the FCMDevice for the user based on their fcm_token
        device, created = FCMDevice.objects.get_or_create(
            registration_id=fcm_token,
            defaults={'type': 'android'}  # or 'ios', depending on the user's device
        )
        # Send the notification
        device.send_message(title=title, body=body)
    else:
        # Handle the case where there is no fcm_token
        print("No FCM token found for the user.")
