from django.urls import path
from .views import create_new_audit_session, get_all_audit_types

urlpatterns = [
    path('get-all-audit-types/', get_all_audit_types),
    path('create-new-audit-session/', create_new_audit_session),
]