from rest_framework import serializers
from .models import AuditSession, AuditType

class AuditSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditSession
        fields = '__all__'

class AuditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditType
        fields = '__all__'