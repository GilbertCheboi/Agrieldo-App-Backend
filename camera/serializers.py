from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import NVR, Stream, JanusStream

User = get_user_model()

# Farmer Serializer
class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add more fields as needed


# NVR Serializer
class NVRSerializer(serializers.ModelSerializer):
    farmer = FarmerSerializer(read_only=True)  # Nested farmer info
    streams = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Related streams

    class Meta:
        model = NVR
        fields = [
            'id', 'name', 'ip_address', 'port', 'username', 'password',
            'farmer', 'streams', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# Stream Serializer
class StreamSerializer(serializers.ModelSerializer):
    nvr = NVRSerializer(read_only=True)  # Nested NVR info
    janus_stream = serializers.PrimaryKeyRelatedField(read_only=True)  # Related JanusStream

    class Meta:
        model = Stream
        fields = [
            'id', 'camera_name', 'rtsp_url', 'janus_stream_id',
            'nvr', 'janus_stream', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# JanusStream Serializer
class JanusStreamSerializer(serializers.ModelSerializer):
    stream = StreamSerializer(read_only=True)  # Nested Stream info

    class Meta:
        model = JanusStream
        fields = [
            'id', 'stream', 'janus_room_id', 'janus_server_url'
        ]
