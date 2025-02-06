# urls.py
from django.urls import path
from .views import  send_html_newsletter_view, SubscribeView

urlpatterns = [
    path('send-html-newsletter/', send_html_newsletter_view, name='send_html_newsletter'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),

]
