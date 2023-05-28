from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.hashers import make_password

from authentication.models import Auditor

# Create your views here.
# reference: https://www.django-rest-framework.org/api-guide/permissions/


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_has_logged_in(request):
    return JsonResponse({"Logged-In": 1})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_logged_in_user_data(request):
    return JsonResponse({"username": request.user.username})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_auditor_id_by_user_id(request, user_id):
    try:
        auditor_id = Auditor.objects.get(user=user_id).id
        data = {
            'auditor_id': auditor_id
        }
    except Auditor.DoesNotExist:
        data = {
            'auditor_id': None
        }
    return JsonResponse(data, safe=False)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_auditor(request, id_auditor):
    auditor = get_object_or_404(Auditor, pk=int(id_auditor))
    id_user = auditor.user.id
    user = get_object_or_404(User, pk=id_user)
    user.delete()
    return JsonResponse({"success": True, "message": f"Akun Auditor {user.username} berhasil dihapus"})
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])  # harus sudah login
def change_password(request):
    id_user = request.POST.get("id_user")
    current_password = request.POST.get("current_password")
    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")
    user = get_object_or_404(User, pk=id_user)
    if user.check_password(current_password):
        if new_password == confirm_password:
            # Set the new password for the user
            user.password = make_password(new_password)
            user.save()
            return HttpResponse("Password berhasil diubah.")
        else:
            return HttpResponse("New password dan confirm password berbeda!")
    else:
        return HttpResponse("Password saat ini salah!")