from django.urls import path

from .views import get_all_audit_types, get_all_auditors, create_new_audit_session, get_audit_categories, post_audit_data, get_audit_question
from audit.views_questions import post_audit_question_session

urlpatterns = [
    path('get-all-audit-types/', get_all_audit_types, name='get_audit_types'),
    path('get-all-auditors/', get_all_auditors),
    path('create-new-audit-session/<str:id>', create_new_audit_session, name='create_audit_session'),
    path('audit-categories/<str:id>', get_audit_categories, name="audit category"),
    path('upload-data', post_audit_data, name="upload data"),
    path('audit-questions/<str:id>', get_audit_question, name='audit question'),
    path('audit-question-session', post_audit_question_session, name="audit-question-session")
]
