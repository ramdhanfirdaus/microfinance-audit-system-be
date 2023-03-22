from django.urls import path
from .views import get_audit_categories, post_audit_data

urlpatterns = [
    path('audit-categories/<str:id>', get_audit_categories, name="audit category"),
    path('upload-data', post_audit_data, name="upload data")
]