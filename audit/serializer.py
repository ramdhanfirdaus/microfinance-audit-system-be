from rest_framework import serializers
from .models import AuditQuestion, AuditType, AuditSession, AuditCategory

class AuditTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditType
        fields = '__all__'

class AuditSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditSession
        fields = ['id', 'type']

class AuditCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditCategory
        fields = '__all__'

class AuditQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditQuestion
        fields = ['id', 'title']
        