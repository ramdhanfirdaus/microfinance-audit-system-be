from django.test import TestCase, override_settings
import unittest
from django.apps import apps
import json
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

import os
import tempfile
import zipfile

from pymongo import MongoClient

from .apps import AuditConfig
from .models import AuditCategory, AuditType, AuditSession
from .serializer import AuditCategorySerializer

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

class PostAuditDataViewTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_audit_data(self):
        # Create a zip file with some test data
        with zipfile.ZipFile(self.temp_file.name, 'w') as zip_ref:
            zip_ref.writestr('file1.txt', 'hello')
            zip_ref.writestr('file2.txt', 'world')

        with open(self.temp_file.name, 'rb') as f:
            response = self.client.post('/audit/upload-data', {'file': f}, format='multipart')

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the files were saved to the child collection
        client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        db = client['masys']
        collection = db['audit_data']
        data_count = collection.count_documents({})
        
        data_name = 'audit-data-' + str(data_count)
        child_collection = collection[data_name]
        self.assertEqual(child_collection.count_documents({}), 2)

