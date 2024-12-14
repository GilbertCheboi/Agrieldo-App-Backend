from django.urls import path
from .views import MessageListCreateView

urlpatterns = [
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
]
