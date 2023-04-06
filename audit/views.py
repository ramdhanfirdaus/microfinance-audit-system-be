from pymongo import MongoClient

import zipfile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import AuditType, AuditCategory, AuditSession
from authentication.models import Auditor
from .serializer import  AuditTypeSerializer, AuditCategorySerializer, AuditSessionSerializer
from authentication.serializer import AuditorSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_audit_types(request): #return all audit types
    types = AuditType.objects.all()
    serializer = AuditTypeSerializer(types, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_auditors(request):
    auditors = Auditor.objects.all()
    serializer = AuditorSerializer(auditors, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def create_new_audit_session(request, id): #create a new audit session with spesific audit type 
    AuditSession.objects.update_or_create(
        type = AuditType.objects.get(id = int(id))
    )
    return HttpResponse(200)

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
def post_audit_data(request):
    zip_file = request.FILES.get('file')

    extracted_data = extract_data(zip_file)

    if(len(extracted_data) == 0) :
        raise ValidationError
    
    client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
    db = client['masys']
    collection = db['audit_data']
    data_count = collection.count_documents({})

    data_name = 'audit-data-'+str(data_count+1)

    collection.insert_one({'name': data_name})
    child_collection = collection[data_name]

    for filename, file_data in extracted_data.items():
        child_collection.insert_one({'filename': filename, 'file_data': file_data})
        
    return Response(data={'message':"File uploaded to database", 'data': data_name}, status=status.HTTP_200_OK)

    

def extract_data(zip_file):
    result_data = dict()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for filename in zip_ref.namelist():
            file_data = zip_ref.read(filename)
            result_data[filename] = file_data

    return result_data