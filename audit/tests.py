from django.test import TestCase
import unittest
from django.apps import apps
import json
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from .apps import AuditConfig
from .models import AuditType, AuditSession
from .serializer import AuditSessionSerializer, AuditTypeSerializer

# Create your tests here.
class AuditAppTestCase(unittest.TestCase):
    def test_apps(self):
        self.assertEqual(AuditConfig.name, 'audit')
        self.assertEqual(apps.get_app_config('audit').name, 'audit')

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

class GetAllAuditTypeViewTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_get_all_audit_type(self):
        response = self.client.get('/audit/get-all-audit-types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class CreateNewAuditSessionViewTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def test_create_new_audit_session(self):
        response = self.client.get('/audit/create-new-audit-session/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
