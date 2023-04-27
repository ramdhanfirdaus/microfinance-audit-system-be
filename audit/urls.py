from django.urls import path

from audit.views.views import get_all_auditors, create_new_audit_session, post_audit_data
from audit.views.views_questions import post_audit_question_session, get_audit_question, get_sample
from audit.views.views_categories import get_audit_categories, post_audit_category, get_all_audit_categories
from audit.views.views_types import get_all_audit_types, post_audit_type

urlpatterns = [
    path('create-audit-type', post_audit_type, name='create audit type'),
    path('get-all-audit-types/', get_all_audit_types, name='get_audit_types'),
    path('get-all-auditors/', get_all_auditors),
    path('create-new-audit-session/<str:id>', create_new_audit_session, name='create_audit_session'),
    path('create-audit-category', post_audit_category, name="create audit category"),
    path('get-all-audit-categories/', get_all_audit_categories, name="get_audit_categories"),
    path('audit-categories/<str:id>', get_audit_categories, name="audit category"),
    path('upload-data', post_audit_data, name="upload data"),
    path('audit-questions/<str:id>', get_audit_question, name='audit question'),
    path('sample-data', get_sample, name="sample data"),
    path('audit-question-session', post_audit_question_session, name="audit-question-session")
]
