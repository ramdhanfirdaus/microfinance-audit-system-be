from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

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


