from django.urls import path
from .views import EventListCreateView, EventDetailView, user_role

urlpatterns = [
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('user-role/', user_role, name='user-role'),

]
