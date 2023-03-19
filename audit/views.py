from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser

from .models import AuditCategory, AuditSession, AuditType
from .serializer import AuditCategorySerializer, AuditSession, AuditSessionSerializer

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

@api_view(['POST'])
def create_audit_session(request, id):
    # making sure that type exist
    try :
        types = AuditType.objects.filter(id = int(id))
        if len(types) == 0 :
            raise ObjectDoesNotExist        
    except ObjectDoesNotExist :
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    # create session
    data = JSONParser().parse(request)
    serializer = AuditSessionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)