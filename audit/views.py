from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status

import zipfile

from pymongo import MongoClient

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import AuditCategory
from .serializer import AuditCategorySerializer

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
