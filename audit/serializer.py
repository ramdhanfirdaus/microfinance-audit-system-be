from rest_framework import serializers
from .models import AuditQuestion, AuditType, AuditSession, AuditCategory, AuditHistory
import ast


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
        fields = ['id', 'title', 'query']


class AuditorsNameField(serializers.Field):
    def to_representation(self, value):
        return ast.literal_eval(value.auditors_name)


class SessionDateField(serializers.Field):
    def to_representation(self, value):
        return value.session_date.strftime("%d-%m-%Y")


class DateField(serializers.Field):
    def to_representation(self, value):
        return value.date.strftime("%d-%m-%Y")


class AuditHistorySerializer(serializers.ModelSerializer):
    session_date = SessionDateField(source='*')
    date = DateField(source='*')
    auditors_name = AuditorsNameField(source='*')

    class Meta:
        model = AuditHistory
        fields = ['id', 'list_auditor', 'auditors_name', 'audit_session', 'session_date', 'date']
