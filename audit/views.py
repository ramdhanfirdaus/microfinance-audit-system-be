from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .models import AuditSession, AuditType, AuditCategory
from .serializer import AuditSessionSerializer, AuditTypeSerializer, AuditCategorySerializer

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

@api_view(['GET'])
def get_audit_categories(request, id):
    print(id)

    try :
        audit_categories = AuditCategory.objects.filter(audit_type = int(id))

        if len(audit_categories) == 0 :
            raise ObjectDoesNotExist
        
    except ObjectDoesNotExist :
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = AuditCategorySerializer(audit_categories, many=True)
    return Response(serializer.data)


