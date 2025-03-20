import requests
import logging
from django.conf import settings

def send_sms(message, mobile):
    """
    Sends an SMS using the Celcom Africa SMS API.
    
    :param message: The message to send
    :param mobile: The recipient's phone number
    """
    url = "https://isms.celcomafrica.com/api/services/sendsms"
    payload = {
        "apikey": settings.SMS_API_KEY,  
        "partnerID": settings.SMS_PARTNER_ID,  
        "message": message,
        "shortcode": settings.SMS_SHORTCODE, 
        "mobile": mobile
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()  
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send SMS: {e}")
        return None
