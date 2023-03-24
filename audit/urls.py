from django.urls import path
from .views import get_all_audit_types, create_new_audit_session

urlpatterns = [
    path('get-all-audit-types/', get_all_audit_types, name="get_audit_types"),
    path('create-new-audit-session/<str:id>', create_new_audit_session, name='create_audit_session'),
]