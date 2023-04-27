from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST, require_GET
from pymongo import MongoClient

from audit.models import AuditCategory, AuditType
from audit.serializer import  AuditCategorySerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_audit_categories(request):
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_audit_category(request):
    pass
