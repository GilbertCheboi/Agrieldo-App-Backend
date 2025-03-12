from rest_framework import serializers
from .models import Machinery, MachineryUsageLog, MaintenanceLog, FuelLog, SparePart, Alert


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

