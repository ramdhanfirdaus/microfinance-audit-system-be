from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, MinLengthValidator

from authentication.validators import *
from .models import Auditor

# Register serializer

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'username': {
                'max_length': 50,
                'validators': [MinLengthValidator(3),
                                validate_unique_username],
            },
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {
                'validators': [validate_unique_email],
            }
        }

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        validate_username_password(username, password)

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],     
                                        password=validated_data['password'],
                                        first_name=validated_data['first_name'],  
                                        last_name=validated_data['last_name'],
                                        email=validated_data['email'])
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