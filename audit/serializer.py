from rest_framework import serializers
from .models import *

class AuditCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditCategory
        fields = '__all__'