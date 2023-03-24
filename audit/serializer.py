from rest_framework import serializers
from .models import AuditType, AuditSession

class AuditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditType
        fields = '__all__'

class AuditSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditSession
        fields = ['id', 'type']