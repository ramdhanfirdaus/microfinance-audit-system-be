from rest_framework import serializers
from .models import AuditCategory, AuditSession, AuditType

class AuditCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditCategory
        fields = '__all__'

class AuditSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditSession
        fields = '__all__'

class AuditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditType
        fields = '__all__'