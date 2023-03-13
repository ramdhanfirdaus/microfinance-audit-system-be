from django.test import TestCase
import unittest
from django.apps import apps

from .apps import AuditConfig
from .models import AuditCategory, AuditType

# Create your tests here.
class AuditAppTestCase(unittest.TestCase):
    def test_apps(self):
        self.assertEqual(AuditConfig.name, 'audit')
        self.assertEqual(apps.get_app_config('audit').name, 'audit')

class AuditCategoryModelTestCase(unittest.TestCase):
    #def setUp(self):
    #    self.title = "Kredit"

    #    self.obj = AuditCategory(title = self.title)

    #def test_create_audit_category(self):
    #    assert isinstance(self.obj, AuditCategory)
    
    #def test_field_category(self):
    #    assert self.title == self.obj.title
    pass

class AuditTypeModelTestCase(unittest.TestCase):
    def setUp(self):
        self.label = "General"
        #self.category = [{'label' : 'Kredit'}, 
        #                  {'label': 'Utang'}]
        self.obj = AuditType.objects.create(label = self.label)

    def test_create_audit_type(self):
        assert isinstance(self.obj, AuditType)
    
    def test_field_type(self):
        assert self.label == self.obj.label

    #def test_field_category(self):
    #    assert self.category[1] == self.obj.category[1]
    #    assert self.category[2] == self.obj.category[2]