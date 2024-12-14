from rest_framework import serializers
from .models import EducationalMaterial

class EducationalMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalMaterial
        fields = ['title', 'content', 'file']
