from django.conf import settings
from django.db import models


class NVR(models.Model):
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nvrs'
    )
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(protocol='both')
    port = models.PositiveIntegerField(default=554)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class Stream(models.Model):
    nvr = models.ForeignKey(
        NVR,
        on_delete=models.CASCADE,
        related_name='streams'
    )
    camera_name = models.CharField(max_length=100)
    rtsp_url = models.URLField()
    janus_stream_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.camera_name} - {self.rtsp_url}"


class JanusStream(models.Model):
    stream = models.OneToOneField(
        Stream,
        on_delete=models.CASCADE,
        related_name='janus_stream'
    )
    janus_room_id = models.PositiveIntegerField()
    janus_server_url = models.URLField()

    def __str__(self):
        return f"Janus Stream {self.janus_room_id} ({self.stream.camera_name})"



from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)  # Title of the video
    description = models.TextField(blank=True, null=True)  # Optional description
    file = models.FileField(upload_to='videos/')  # File path in the media directory
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp for upload
    duration = models.PositiveIntegerField(blank=True, null=True)  # Optional, in seconds
    views = models.PositiveIntegerField(default=0)  # Track number of views

    def __str__(self):
        return self.title

