from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse

from audit.models import AuditType
from audit.serializer import  AuditTypeSerializer

@require_GET
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
    label = request.POST.get('label')
    if label:
        existing_audit_type = AuditType.objects.filter(label__iexact=label).first()
        if existing_audit_type:
            return JsonResponse({'error': 'Sudah ada kategori dengan nama yang sama'}, status=400)
        audit_type = AuditType(label=label)
        audit_type.save()
        return JsonResponse({'success': True, 'message': f'berhasil manambahkan tipe audit "{label}"'})
    else:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)

