from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse

from .models import AuditType, AuditSession
from .serializer import  AuditTypeSerializer, AuditSessionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_audit_types(request): #return all audit types
    types = AuditType.objects.all()
    serializer = AuditTypeSerializer(types, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def create_new_audit_session(request, id): #create a new audit session with spesific audit type 
    AuditSession.objects.update_or_create(
        type = AuditType.objects.get(id = int(id))
    )
    return HttpResponse(200)