import io
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.http import require_GET, require_POST
from django.template.loader import get_template
from xhtml2pdf import pisa

import re

from audit.models import AuditHistory
from audit.serializer import AuditHistorySerializer
from authentication.models import Auditor, User
from audit.dto.pdf_dto import PdfDTO


@require_GET
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_history(request):
    user = User.objects.get(username=request.user.username)

    if user.is_staff:
        return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    auditor = Auditor.objects.get(user_id=request.user.id)
    audit_history_list = []
    for history_id in re.findall(r"(\d+),?", auditor.list_history):
        audit_history_list.append(AuditHistory.objects.get(id=history_id))
    audit_history_list = AuditHistorySerializer(audit_history_list, many=True)

    return Response(audit_history_list.data, status=status.HTTP_200_OK)


@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_result_html(request):
    history_id = request.POST.get('history_id')

    try:
        html = get_html(history_id)
        return HttpResponse(html)
    except TemplateDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND, content='Template not found')
    except Exception as e:
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f'Error generating HTML: {str(e)}')

@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def download_result_pdf(request):
    history_id = request.POST.get('history_id')

    try:
        html = get_html(history_id)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            return response

    except TemplateDoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND, content='Template not found')
    except Exception as e:
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f'Error generating HTML: {str(e)}')

def get_html(history_id):
    history = AuditHistory.objects.get(id=int(history_id))
    pdf_dto = PdfDTO(history)
    template = get_template('audit/template.html')
    html = template.render({'dto': pdf_dto})
    return html
    