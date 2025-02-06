"""
URL configuration for farm_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/messaging/', include('messaging.urls')),
    path('api/market/', include('market.urls')),
    path('api/store/', include('store.urls')),
    path('api/education/', include('education.urls')),
    path('api/animals/', include('animals.urls')),  # Changed to a specific path for clarity
    path('api/farms/', include('farms.urls')),      # Ensured no duplicate path for farms
    path('api/vet_requests/', include('vet_requests.urls')),  # Added path for vet_request app
    path('api/finances/', include('finances.urls')),
    path('api/feed/', include('feed.urls')),  # Include finances app URLs
    path('api/profiles/', include('profiles.urls')),  # Include profile URLs
    path('api/production/', include('production.urls')),  # Include profile URLs
    path('api/camera/', include('camera.urls')),  # Include profile URLs
    path('api/Subscriber/', include('Subscriber.urls')),  # Include profile URLs
    path('api/merchandise/', include('merchandise.urls')),  # Include merchandise app URLs
    path('api/feed_store/', include('feed_store.urls')),  # Include feed_store app URLs
    path('api/drug_store/', include('drug_store.urls')),  # Include drug_store app URLs
    path('api/calendar/', include('calendar_app.urls')),  # Include calendar_app app URLs





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
