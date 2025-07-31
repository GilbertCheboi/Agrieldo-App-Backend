from rest_framework import serializers
from .models import Machinery, MachineryUsageLog, MaintenanceLog, FuelLog, SparePart, Alert, MachineryVendorApplication, MachineryOrder

class MachineryUsageLogSerializer(serializers.ModelSerializer):
    machinery_name = serializers.ReadOnlyField(source="machinery.name")  # To show machinery name in response

    class Meta:
        model = MachineryUsageLog
        fields = ["id", "machinery", "machinery_name", "usage_date", "hours_used", "operator", "description", "fuel_consumed", "created_at"]

class MachinerySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())  # ✅ Auto-assigns owner

    class Meta:
        model = Machinery
        fields = ['id', 'name', 'model', 'purchase_date', 'condition', 'image', 'owner']


class MaintenanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceLog
        fields = '__all__'

class FuelLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelLog
        fields = '__all__'

class SparePartSerializer(serializers.ModelSerializer):
    class Meta:
        model = SparePart
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'



class MachineryVendorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryVendorApplication
        # explicitly list fields (or add price_per_day if you’re using `__all__`)
        fields = [
            'id', 'user', 'name', 'phone_number',
            'type_of_machine', 'model', 'price_per_day',
            'latitude', 'longitude', 'submitted_at',
            'approved', 'is_active',
        ]
        read_only_fields = ['id', 'user', 'submitted_at', 'approved', 'is_active']

class MachineryOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryOrder
        # only the fields your frontend sends:
        fields = [
            'customer_name',
            'customer_phone',
            'land_size_acres',
            'notes',
            'start_date',
            'end_date',
        ]
        read_only_fields = ['id']


class MachineryOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryOrder
        # only the fields your frontend sends:
        fields = [
            'customer_name',
            'customer_phone',
            'land_size_acres',
            'notes',
            'start_date',
            'end_date',
        ]


