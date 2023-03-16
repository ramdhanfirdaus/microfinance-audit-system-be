from django.urls import path
from .views import get_audit_categories

urlpatterns = [
    path('audit-categories/<str:id>', get_audit_categories, name="audit category")
]