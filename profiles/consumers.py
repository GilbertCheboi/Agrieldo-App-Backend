import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class VetLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vet_id = self.scope['url_route']['kwargs']['vet_id']
        self.room_group_name = f'vet_location_{self.vet_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data['latitude']
        longitude = data['longitude']
        await self.update_vet_location(self.vet_id, latitude, longitude)

    @sync_to_async
    def update_vet_location(self, vet_id, latitude, longitude):
        from .models import Vet  # Import here to avoid the AppRegistryNotReady error

        vet = Vet.objects.get(id=vet_id)
        vet.latitude = latitude
        vet.longitude = longitude
        vet.save()


class FarmerLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.farmer_id = self.scope['url_route']['kwargs']['farmer_id']
        self.room_group_name = f'farmer_location_{self.farmer_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data['latitude']
        longitude = data['longitude']
        await self.update_farmer_location(self.farmer_id, latitude, longitude)

    @sync_to_async
    def update_farmer_location(self, farmer_id, latitude, longitude):
        from .models import  Farmer  # Import here to avoid the AppRegistryNotReady error

        farmer = Farmer.objects.get(id=farmer_id)
        farmer.latitude = latitude
        farmer.longitude = longitude
        farmer.save()

