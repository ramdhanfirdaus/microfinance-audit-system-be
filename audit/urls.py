from django.urls import path
from .views import get_all_audit_types, create_new_audit_session, get_audit_categories, post_audit_data, get_audit_question

urlpatterns = [
    path('get-all-audit-types/', get_all_audit_types, name='get_audit_types'),
    path('create-new-audit-session/<str:id>', create_new_audit_session, name='create_audit_session'),
    path('audit-categories/<str:id>', get_audit_categories, name='audit category'),
    path('upload-data', post_audit_data, name='upload data'),
    path('audit-questions/<str:id>', get_audit_question, name='audit question')
]
