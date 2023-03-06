from django.test import TestCase
from django.apps import apps

from .apps import AuditConfig
from .models import AuditCategory, AuditType

# Create your tests here.
class AuditAppTestCase(TestCase):
    def test_apps(self):
        self.assertEqual(AuditConfig.name, 'audit')
        self.assertEqual(apps.get_app_config('audit').name, 'audit')

class AuditCategoryModelTestCase(TestCase):
    def setUp(self):
        self.label = "Kredit"

        self.obj = AuditCategory.objects.create(label = self.label)

    def test_create_audit_category(self):
        assert isinstance(self.obj, AuditCategory)
    
    def test_field_category(self):
        assert self.label == self.obj.label

class AuditTypeModelTestCase(TestCase):
    def setUp(self):
        self.label = "General"
        self.obj = AuditType.objects.create(label = self.label)

    def test_create_audit_type(self):
        assert isinstance(self.obj, AuditType)
    
    def test_field_type(self):
        assert self.label == self.obj.label