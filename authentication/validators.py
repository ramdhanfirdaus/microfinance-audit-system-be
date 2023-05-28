# Insert your validator codes here
from rest_framework import serializers
from django.contrib.auth.models import User

def validate_unique_username(username):
    if User.objects.filter(username=username).exists():
        raise serializers.ValidationError("Username already exists.")
    
def validate_unique_email(email):
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email already exists.")
    
def validate_username_password(username, password):
    if username == password:
        raise serializers.ValidationError("Username and password should not be the same.")
