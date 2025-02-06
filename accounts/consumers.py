# farm_management/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

class UserLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        WebSocket connection method.
        This is called when a WebSocket connection is made.
        """
        User = get_user_model()  # Get the User model
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        await self.accept()
        print(f"WebSocket connection established for user {self.user_id}")  # Print for debugging

    async def disconnect(self, close_code):
        """
        WebSocket disconnect method.
        This is called when the WebSocket connection is closed.
        """
        print(f"WebSocket connection closed for user {self.user_id}")  # Print for debugging

    async def receive(self, text_data):
        """
        WebSocket receive method.
        This is called when a message is received over the WebSocket.
        """
        try:
            # Attempt to parse the incoming WebSocket message
            data = json.loads(text_data)
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            # Check if both latitude and longitude are provided
            if latitude is None or longitude is None:
                print("Error: Latitude or longitude not provided in WebSocket message.")  # Print for debugging
                return

            # Log the received latitude and longitude
            print(f"Received latitude: {latitude}, longitude: {longitude}")  # Print for debugging

            # Try updating the user's location
            await self.update_user_location(self.user_id, latitude, longitude)
            print(f"Updated User {self.user_id} location to ({latitude}, {longitude})")  # Print for debugging

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")  # Print for debugging

        except Exception as e:
            print(f"Unexpected error while processing WebSocket data: {e}")  # Print for debugging

    @sync_to_async
    def update_user_location(self, user_id, latitude, longitude):
        """
        This method updates the user's location in the database asynchronously.
        """
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            user.latitude = latitude
            user.longitude = longitude
            user.save()
            user.refresh_from_db()  # Ensure fields are updated
            print(f"Location for user {user_id} successfully saved: ({user.latitude}, {user.longitude})")  # Print for debugging
        except User.DoesNotExist:
            print(f"User with ID {user_id} does not exist.")  # Print for debugging
            raise User.DoesNotExist(f"User with ID {user_id} does not exist.")

