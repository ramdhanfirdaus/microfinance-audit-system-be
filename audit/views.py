from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .models import AuditSession, AuditType
from .serializer import AuditSessionSerializer, AuditTypeSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_audit_types(request):
    types = AuditType.objects.all()
    serializer = AuditTypeSerializer(types, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_new_audit_session(request, id):
    types = AuditType.objects.get(id = int(id))
    serializer = AuditSessionSerializer(type=types)
    return JsonResponse(serializer.data, status=201)