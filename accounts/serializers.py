from rest_framework import serializers
from .models import User, PasswordResetToken
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth import get_user_model
from .models import PasswordResetToken
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'confirm_password', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_user_type(self, value):
        # Map string inputs to integer values if needed
        if value == 'Farmer':
            return User.FARMER
        elif value == 'Vet':
            return User.VET
        elif value == 'Staff':
            return User.STAFF  # Handle 'Staff' as well
        elif value in [User.FARMER, User.VET, User.STAFF]:  # Allow integers directly
            return value
        else:
            raise serializers.ValidationError("Invalid user type.")


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number is already in use.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        # Remove confirm_password as we don't need to save it
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            user_type=validated_data['user_type']
        )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()

class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
