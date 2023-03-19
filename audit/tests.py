from django.test import TestCase
import unittest
from django.apps import apps
import json
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .apps import AuditConfig
from .models import AuditCategory, AuditType, AuditSession
from .serializer import AuditCategorySerializer, AuditSessionSerializer, AuditTypeSerializer

# Create your tests here.
class AuditAppTestCase(unittest.TestCase):
    def test_apps(self):
        self.assertEqual(AuditConfig.name, 'audit')
        self.assertEqual(apps.get_app_config('audit').name, 'audit')

class AuditCategoryModelTestCase(unittest.TestCase):
    def setUp(self):
        self.title = "Kredit"

        self.typeobj = AuditType(label = "General")

        self.obj = AuditCategory(title = self.title, audit_type = self.typeobj)

    def test_create_audit_category(self):
        assert isinstance(self.obj, AuditCategory)
    
    def test_field_category(self):
        assert self.title == self.obj.title

    def test_field_audittype(self):
        assert self.typeobj == self.obj.audit_type

class AuditTypeModelTestCase(unittest.TestCase):
    def setUp(self):
        self.label = "General"
        self.obj = AuditType(label = self.label)

    def test_create_audit_type(self):
        assert isinstance(self.obj, AuditType)
    
    def test_field_type(self):
        assert self.label == self.obj.label

class AuditSessionModelTestCase(unittest.TestCase):
    def setUp(self):
        self.type_ = "General"
        self.type = AuditType.objects.create(label = self.type_)
        self.obj = AuditSession.objects.create(type = self.type)
    
    def test_create_audit_session(self):
        assert isinstance(self.obj, AuditSession)
    
    def test_field_type(self):
        assert self.type == self.obj.type 
        
class AuditCategorySerializerTestCase(unittest.TestCase):
    def setUp(self):
       self.title = "Some Audit Category"
       self.typeobj = AuditType(label = "General")
       self.obj = AuditCategory(title = self.title, audit_type = self.typeobj)

    def test_audit_category_serializer(self):
        serializer_data = AuditCategorySerializer(instance=self.obj).data
        expected_data = {
            'id': self.obj.id,
            'title': 'Some Audit Category',
            'audit_type': self.typeobj.id,
        }
        assert serializer_data == expected_data

class GetAuditCategoriesViewTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.audit_type = AuditType.objects.create(label='Some Audit Type')
        self.audit_category = AuditCategory.objects.create(title='Some Audit Category', audit_type=self.audit_type)
    
    def test_get_audit_categories_view(self):
        response = self.client.get('/audit/audit-categories/'+str(self.audit_type.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        serializer_data = AuditCategorySerializer([self.audit_category], many=True).data
        self.assertEqual(response.data, serializer_data)
    
    def test_get_audit_categories_view_with_invalid_audit_type(self):
        response = self.client.get('/audit/audit-categories/1101')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AuditSessionSerializerTestCase(unittest.TestCase):
    def setUp(self):
       self.type_obj = AuditType(label = "General")
       self.obj = AuditSession(type = self.type_obj)

    def test_audit_session_serializer(self):
        fetched_data = AuditSessionSerializer(instance=self.obj).data
        expected_data = {
            'id': self.obj.id,
            'type': self.type_obj.id,
        }
        assert fetched_data == expected_data

class CreateAuditSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.type_obj = AuditType(label = "General")
        self.obj = AuditSession(type = self.type_obj)
    
    def create_audit_session_view_test(self):
        response = self.client.post('/create-session/'+str(self.type_obj.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        serializer_data = AuditSessionSerializer([self.obj]).data
        self.assertEqual(response.data, serializer_data)

class AuditTypeSerializerTestCase(unittest.TestCase):
    def setUp(self):
       self.label = "Special"
       self.obj = AuditType(label = self.label)

    def test_audit_type_serializer(self):
        fetched_data = AuditTypeSerializer(instance=self.obj).data
        expected_data = {
            'id': self.obj.id,
            'label': self.label,
        }
        assert fetched_data == expected_data