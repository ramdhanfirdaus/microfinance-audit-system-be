from django.shortcuts import render
from django.contrib import auth
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.
# reference: https://www.django-rest-framework.org/api-guide/permissions/


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_has_logged_in(request):
    return JsonResponse({"Logged-In": 1})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_logged_in_user_data(request):
    pass
