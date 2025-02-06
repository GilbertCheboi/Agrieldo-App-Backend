from django.contrib import admin
from .models import NVR, Stream, JanusStream, Video

@admin.register(NVR)
class NVRAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ip_address', 'port', 'farmer', 'created_at')
    search_fields = ('name', 'ip_address', 'farmer__username')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'ip_address', 'port', 'username', 'password', 'farmer')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'camera_name', 'rtsp_url', 'nvr', 'created_at')
    search_fields = ('camera_name', 'rtsp_url', 'nvr__name')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('camera_name', 'rtsp_url', 'janus_stream_id', 'nvr')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(JanusStream)
class JanusStreamAdmin(admin.ModelAdmin):
    list_display = ('id', 'janus_room_id', 'janus_server_url', 'stream')
    search_fields = ('janus_room_id', 'janus_server_url', 'stream__camera_name')
    list_filter = ('stream__nvr__farmer',)
    fieldsets = (
        (None, {
            'fields': ('stream', 'janus_room_id', 'janus_server_url')
        }),
    )

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'views')
    search_fields = ('title',)
