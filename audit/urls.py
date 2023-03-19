from django.urls import path
from .views import get_all_audit_types

urlpatterns = [
    path('get-all-audit-types/', get_all_audit_types),
]