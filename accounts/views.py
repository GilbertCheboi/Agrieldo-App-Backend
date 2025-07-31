from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from profiles.models import Farmer, Vet, Staff, MechanizationAgent  
from machinery.models import MachineryVendorApplication
from .serializers import UserRegistrationSerializer, UserSerializer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .serializers import PasswordResetRequestSerializer, PasswordResetSerializer
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import send_mail
from .models import User, PasswordResetToken
from rest_framework.views import APIView
from rest_framework import generics, permissions

import firebase_admin
from firebase_admin import credentials, auth
import re







#User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # Extract user registration data
        user_type = request.data.get('user_type')  # Expect 1 for Farmer, 2 for Vet
        phone_number = request.data.get('phone_number', '')  # ✅ Define it here

        # Check required fields
        if not user_type:
            return Response({"error": "User type is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the user using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create a Farmer or Vet profile based on user_type
        if user_type == "1":  # Farmer
            Farmer.objects.create(user=user, phone_number=request.data.get('phone_number', ''))
            print("Farmer profile created")  # Debugging line
        elif user_type == "3":  # Staff
            Staff.objects.create(user=user, phone_number=request.data.get('phone_number', ''))
            print("Staff profile created")  # Debugging line


        elif user_type == "2":  # Vet
            Vet.objects.create(
                user=user,
                phone_number=request.data.get('phone_number', ''),
            )
            print("Vet profile created")  # Debugging line
        
        elif user_type == "4":  # Mechanization Agent (Vendor)
            MechanizationAgent.objects.create(
                user=user,
                phone_number=phone_number,
            )
        else:
            return Response({"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Call the default post method to get tokens
        response = super().post(request, *args, **kwargs)

        # Fetch the user from the request
        try:
            username = request.data.get('username')
            user = User.objects.get(username=username)
            # Determine user type based on associated profile model
            if hasattr(user, 'farmer_profile'):
                user_type = 'farmer'
            elif hasattr(user, 'vet_profile'):
                user_type = 'vet'
            elif hasattr(user, 'staff_profile'):
                user_type = 'staff'
            elif hasattr(user, 'mechanization_agent_profile'):
                user_type = 'mechanization_agent'

            else:
                user_type = 'unknown'
            user_id = user.id  # Get user ID directly from the user instance
            

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Add user_type to the response data
        response.data['user_type'] = user_type
        response.data['user_id'] = user_id  # Unified user_id for both farmer and vet



        return response
@login_required
def update_fcm_token(request):
    fcm_token = request.POST.get('fcm_token')
    if fcm_token:
        request.user.fcm_token = fcm_token
        request.user.save()
        return JsonResponse({"message": "FCM token updated successfully."})
    return JsonResponse({"error": "FCM token is required."}, status=400)





class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to make this request

    def post(self, request):
        email_or_phone = request.data.get('email_or_phone')

        if not email_or_phone:
            return Response({"error": "Email or phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if input is email or phone number
        is_email = bool(re.match(r"[^@]+@[^@]+\.[^@]+", email_or_phone))  # Simple email regex
        is_phone = bool(re.match(r"^\+?[1-9]\d{1,14}$", email_or_phone))  # Valid phone number regex (E.164 format)

        if is_email:
            user = User.objects.filter(email=email_or_phone).first()
            if not user:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

            # Generate a reset code
            reset_code = get_random_string(length=6, allowed_chars='0123456789')  # A 6-digit code
            PasswordResetToken.objects.create(user=user, token=reset_code)

            # Send the reset code to the user's email
            reset_message = f'Your password reset code for Agrieldo is: {reset_code}. Use this code to reset your password.'
            send_mail(
                'Password Reset Code',  # Subject
                reset_message,  # Body
                settings.DEFAULT_FROM_EMAIL,  # From email address (configured in settings.py)
                [user.email],  # Recipient email address
                fail_silently=False,  # Whether to silently fail if there's an issue with sending the email
            )

            return Response({"message": "A reset code has been sent to your email."}, status=status.HTTP_200_OK)

        elif is_phone:
            # Handle phone number-based password reset using Firebase
            try:
                # Firebase expects a "phone number verification" approach
                reset_code = get_random_string(length=6, allowed_chars='0123456789')  # Generate a reset code
                
                # Save the token to the database with the phone number (no associated user yet)
                PasswordResetToken.objects.create(user=None, token=reset_code, phone_number=email_or_phone)
                print(f"Sending SMS to {phone_number} with code {reset_code}")

                # Send SMS using Firebase Authentication
                # Firebase requires you to generate a verification code
                phone_number = email_or_phone  # The phone number entered by the user
                print(f"Processing reset for phone number: {phone_number}")

                message = f'Your password reset code for Agrieldo is: {reset_code}'

                # Send verification code to phone number
                # Firebase Admin SDK will not send the SMS directly, so you'll need a 3rd party service like Twilio or Firebase Functions
                # In this case, you'd typically trigger a Firebase Function or use another API like Twilio to send the SMS

                # This is where you would integrate Firebase Functions or another SMS provider (e.g., Twilio) for sending SMS.
                # For Firebase Function: Call it to send SMS with the reset code.
                print(f'SMS to {phone_number}: {message}')

                return Response({"message": "A reset code has been sent to your phone number."}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": f"Failed to send SMS: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response({"error": "Invalid email or phone number."}, status=status.HTTP_400_BAD_REQUEST)

            
class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response({"error": "Token and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            user = reset_token.user
            user.set_password(new_password)
            user.save()
            reset_token.delete()  # Delete the token after it is used

            return Response({"message": "Your password has been successfully reset."}, status=status.HTTP_200_OK)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """API endpoint to list all users."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

class UserDetailView(generics.RetrieveAPIView):
    """API endpoint to retrieve a single user by ID."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]