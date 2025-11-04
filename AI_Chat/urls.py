from django.urls import path
from .views import (
    ChatSessionListCreateView,
    ChatMessageListCreateView,
    ChatSessionDeleteView,
)

urlpatterns = [
    path("chats/", ChatSessionListCreateView.as_view(), name="chat-session-list-create"),
    path("chats/<int:chat_id>/messages/", ChatMessageListCreateView.as_view(), name="chat-messages"),
    path("chats/<int:chat_id>/", ChatSessionDeleteView.as_view(), name="chat-delete"),
]

