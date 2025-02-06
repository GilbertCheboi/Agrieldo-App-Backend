from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from profiles.models import Farmer, Vet

User = get_user_model()

class Command(BaseCommand):
    help = 'Create missing profiles for existing users'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if hasattr(user, 'user_type'):
                if user.user_type == "1" and not hasattr(user, 'farmer_profile'):
                    Farmer.objects.create(user=user, phone_number=user.phone_number)
                    self.stdout.write(self.style.SUCCESS(f"Created Farmer profile for user {user.username}"))
                elif user.user_type == "2" and not hasattr(user, 'vet_profile'):
                    Vet.objects.create(user=user, phone_number=user.phone_number)
                    self.stdout.write(self.style.SUCCESS(f"Created Vet profile for user {user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"User {user.username} has no user_type, skipping."))
