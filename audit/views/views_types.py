from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.http import require_POST
from django.http import JsonResponse

from audit.models import AuditType
from audit.serializer import  AuditTypeSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_audit_types(request): #return all audit types
    types = AuditType.objects.all()
    serializer = AuditTypeSerializer(types, many=True)
    return JsonResponse(serializer.data, safe=False)

@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_audit_type(request):
    pass

