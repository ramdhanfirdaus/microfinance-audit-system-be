from django.urls import path
from .views import get_audit_categories, create_audit_session

urlpatterns = [
    path('audit-categories/<str:id>', get_audit_categories, name="audit category"),
    path('create-session/<str:id>', create_audit_session, name='create_audit_session'),
]