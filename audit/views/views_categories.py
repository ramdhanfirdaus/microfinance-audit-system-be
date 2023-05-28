from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_GET, require_POST

from audit.models import AuditCategory, AuditType, AuditSession
from audit.serializer import  AuditCategorySerializer

@require_GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_audit_categories(request):
    categories = AuditCategory.objects.all()
    serializer = AuditCategorySerializer(categories, many=True)
    return JsonResponse(serializer.data, safe=False)

@require_GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_categories(request, id):

    try :
        audit_categories = AuditCategory.objects.filter(audit_type = int(id))

        if len(audit_categories) == 0 :
            raise ObjectDoesNotExist
        
    except ObjectDoesNotExist :
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = AuditCategorySerializer(audit_categories, many=True)
    return Response(serializer.data)

@require_GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_categories_by_session(request, session_id):

    try :
        audit_session = AuditSession.objects.get(id=int(session_id))
        audit_categories = AuditCategory.objects.filter(audit_type=audit_session.type)

        if len(audit_categories) == 0 :
            raise ObjectDoesNotExist
        
    except Exception :
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = AuditCategorySerializer(audit_categories, many=True)
    return Response(serializer.data)

@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_audit_category(request):
    title = request.POST.get('title')
    audit_type_id = request.POST.get('audit_type_id')
    if title and audit_type_id:
        existing_audit_category = AuditCategory.objects.filter(title__iexact=title, audit_type_id=audit_type_id).first()
        if existing_audit_category:
            return JsonResponse({'error': 'Sudah ada kategori dengan nama yang sama'}, status=400)
        audit_type = AuditType.objects.get(id=audit_type_id)
        audit_category = AuditCategory(title=title, audit_type=audit_type)
        audit_category.save()
        return JsonResponse({'success': True, 'message': f'berhasil manambahkan kategori audit "{title}"'})
    else:
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
