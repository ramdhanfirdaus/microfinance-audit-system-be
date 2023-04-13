from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Auditor

# Register serializer


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],     password=validated_data['password'],
                                        first_name=validated_data['first_name'],  last_name=validated_data['last_name'])
        return user

# User serializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class AuditorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Auditor
        fields = '__all__'
        depth = 1