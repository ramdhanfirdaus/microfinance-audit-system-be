from django.urls import path
from .views import create_new_audit_session, get_all_audit_types, get_audit_categories, post_audit_data

urlpatterns = [
    path('get-all-audit-types/', get_all_audit_types),
    path('create-new-audit-session/', create_new_audit_session),
    path('audit-categories/<str:id>', get_audit_categories, name="audit category"),
    path('upload-data', post_audit_data, name="upload data")
]