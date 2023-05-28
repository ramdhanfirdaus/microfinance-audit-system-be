from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response

from django.views.decorators.http import require_GET, require_POST
from audit.models import AuditSession, AuditHistory
from authentication.models import Auditor


@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_audit(request):
    id_session = request.POST.get("idSession")
    ids_auditor = [int(auditor_id) for auditor_id in request.POST.get("idsAuditor").split(',')]
    session = AuditSession.objects.get(id=int(id_session))

    if session.is_active:
        session.is_active = False
        session.save()

        history = AuditHistory.objects.create(audit_session=session, session_date=session.date)
        set_auditor_history(ids_auditor, history)

        msg = "Audit Session berhasil diselesaikan."
        return Response(data={'message': msg}, status=status.HTTP_200_OK)
    else:
        msg = "Audit Session telah diselesaikan sebelumnya."
        return Response(data={'message': msg}, status=status.HTTP_403_FORBIDDEN)


def set_auditor_history(ids_auditor, history):
    for id_auditor in ids_auditor:
        set_inactive_auditor(id_auditor, history.id)
        set_history_list_auditor(history, id_auditor)
        set_history_auditors_name(history, id_auditor)


def set_inactive_auditor(id_auditor, id_history):
    auditor = Auditor.objects.get(id=int(id_auditor))

    list_history = eval(auditor.list_history)
    list_history.append(id_history)

    auditor.list_history = str(list_history)
    auditor.on_audit = False
    auditor.session = None

    auditor.save()


def set_history_list_auditor(history, id_auditor):
    list_auditor = eval(history.list_auditor)
    list_auditor.append(id_auditor)
    history.list_auditor = str(list_auditor)
    history.save()

def set_history_auditors_name(history, id_auditor):
    auditor = Auditor.objects.get(id=int(id_auditor))
    name = auditor.user.first_name + " " + auditor.user.last_name
    
    auditors_name_list = eval(history.auditors_name)
    auditors_name_list.append(name)
    history.auditors_name = str(auditors_name_list)

    history.save()

@require_GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auditors_by_session(request, id_session, user_id):
    try:
        session = AuditSession.objects.get(id=int(id_session))
        if not session.is_active:
            msg = "Audit Session telah diselesaikan."
            return Response(data={'message': msg}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        msg = "Audit Session tidak ditemukan."
        return Response(data={'message': msg}, status=status.HTTP_404_NOT_FOUND)

    auditors = Auditor.objects.filter(session=int(id_session))

    flag, lst_name, lst_id = cek_auditors(user_id, auditors)

    if flag:
        data = {
            'nama': lst_name,
            'id': lst_id
        }

        return JsonResponse(data, safe=False)
    else:
        msg = "Anda tidak memiliki akses pada sesi audit ini."
        return Response(data={'message': msg}, status=status.HTTP_403_FORBIDDEN)


def cek_auditors(user_id, auditors):
    lst_name = []
    lst_id = []
    flag = False
    for auditor in auditors:
        name = auditor.user.first_name + " " + auditor.user.last_name
        lst_name.append(name)
        lst_id.append(auditor.id)
        if int(user_id) == auditor.user_id:
            flag = True

    return flag, ', '.join(lst_name), lst_id


@require_GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_by_auditor(request, user_id):
    auditors = Auditor.objects.get(user=int(user_id))
    session = auditors.session

    if session:
        data = {'id_session': session.id}
    else:
        data = {'message': "Anda tidak memiliki sesi audit aktif."}

    return JsonResponse(data, safe=False)