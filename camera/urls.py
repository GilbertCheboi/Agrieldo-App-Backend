from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NVRViewSet, StreamViewSet, JanusStreamViewSet, VideoListView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'nvrs', NVRViewSet, basename='nvr')
router.register(r'streams', StreamViewSet, basename='stream')
router.register(r'janus-streams', JanusStreamViewSet, basename='janus-stream')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),  # Include all router-generated URLs
    path('videos/', VideoListView.as_view(), name='video_list'),  # Add the video list endpoint
]

