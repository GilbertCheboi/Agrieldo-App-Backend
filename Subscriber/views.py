from django.http import JsonResponse
from django.template.loader import render_to_string
from .utils import  send_html_newsletter
from .models import Subscriber
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny  # Allows any user to access the view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SubscriberSerializer
from django.shortcuts import render, redirect
from .models import Newsletter
from django.http import HttpResponse

class SubscribeView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email already exists in the database
        if Subscriber.objects.filter(email=email).exists():
            return Response({'detail': 'Email is already subscribed.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new subscriber
        Subscriber.objects.create(email=email)
        return Response({'detail': 'Subscription successful!'}, status=status.HTTP_201_CREATED)


def send_html_newsletter_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        html_content = render_to_string('newsletters/newsletter_template.html', {'data': {}})
        recipient_list = Subscriber.objects.filter(is_active=True).values_list('email', flat=True)
        send_html_newsletter(subject, html_content, recipient_list)
        return JsonResponse({'status': 'HTML Newsletter sent successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)



def create_newsletter(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        content = request.POST['content']
        html_content = request.POST['html_content']
        newsletter = Newsletter.objects.create(subject=subject, content=content, html_content=html_content)
        return redirect('newsletter_list')
    return render(request, 'create_newsletter.html')

def newsletter_list(request):
    newsletters = Newsletter.objects.all()
    return render(request, 'newsletter_list.html', {'newsletters': newsletters})
