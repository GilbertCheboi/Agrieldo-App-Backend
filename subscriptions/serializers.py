from rest_framework import serializers
from .models import Subscription, Service, Package

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'package', 'number_of_cows', 'payment_status']

class IndexedServiceSerializer(serializers.ModelSerializer):
    index = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['index', 'id', 'name']

    def get_index(self, obj):
        return self.context['service_index_map'].get(obj.id)

class PackageSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = ['id', 'name', 'price', 'services', 'created_at', 'updated_at']

    def get_services(self, obj):
        services = obj.services.all()
        service_index_map = {service.id: i + 1 for i, service in enumerate(services)}
        context = self.context.copy()
        context['service_index_map'] = service_index_map
        return IndexedServiceSerializer(services, many=True, context=context).data
