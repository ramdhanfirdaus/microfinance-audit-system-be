from rest_framework.test import APIClient
from rest_framework import status

from django.test import override_settings
from django.apps import apps

from pymongo import MongoClient

import unittest, os, tempfile, zipfile, io, time

from openpyxl import Workbook

from audit.apps import AuditConfig
from audit.models import AuditQuestion, AuditType, AuditSession, AuditCategory
from audit.serializer import AuditQuestionSerializer, AuditTypeSerializer, AuditSessionSerializer, AuditCategorySerializer


class AuditAppTestCase(unittest.TestCase):
    def test_apps(self):
        self.assertEqual(AuditConfig.name, 'audit')
        self.assertEqual(apps.get_app_config('audit').name, 'audit')


class AuditTypeModelTestCase(unittest.TestCase):
    def setUp(self):
        self.label = "General"
        self.obj = AuditType(label=self.label)

    def test_create_audit_type(self):
        assert isinstance(self.obj, AuditType)

    def test_field_type(self):
        assert self.label == self.obj.label


class AuditSessionModelTestCase(unittest.TestCase):
    def setUp(self):
        self.type_ = "General"
        self.type = AuditType.objects.create(label=self.type_)
        self.obj = AuditSession.objects.create(type=self.type)

    def test_create_audit_session(self):
        assert isinstance(self.obj, AuditSession)

    def test_field_type(self):
        assert self.type == self.obj.type


class AuditSessionSerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.type_obj = AuditType(label="General")
        self.obj = AuditSession(type=self.type_obj)

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
        self.obj = AuditType(label=self.label)

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
        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

    def test_get_all_audit_type(self):
        response = self.client.get('/audit/get-all-audit-types/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        audit_types = AuditType.objects.all()
        serializer = AuditTypeSerializer(audit_types, many=True)
        self.assertEqual(data, serializer.data)


class CreateNewAuditSessionViewTestCase(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()
        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")
        self.audit_type = AuditType.objects.create(label="General")

    def test_create_new_audit_session(self):
        type_id = str(self.audit_type.id)
        response = self.client.put('/audit/create-new-audit-session/' + type_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuditCategoryModelTestCase(unittest.TestCase):
    def setUp(self):
        self.title = "Kredit"

        self.typeobj = AuditType(label="General")

        self.obj = AuditCategory(title=self.title, audit_type=self.typeobj)

    def test_create_audit_category(self):
        assert isinstance(self.obj, AuditCategory)

    def test_field_category(self):
        assert self.title == self.obj.title

    def test_field_audittype(self):
        assert self.typeobj == self.obj.audit_type


class AuditCategorySerializerTestCase(unittest.TestCase):
    def setUp(self):
        self.title = "Some Audit Category"
        self.typeobj = AuditType(label="General")
        self.obj = AuditCategory(title=self.title, audit_type=self.typeobj)

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

        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

        self.audit_type = AuditType.objects.create(label='Some Audit Type')
        self.audit_category = AuditCategory.objects.create(title='Some Audit Category', audit_type=self.audit_type)

    def test_get_audit_categories_view(self):
        response = self.client.get('/audit/audit-categories/' + str(self.audit_type.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = AuditCategorySerializer([self.audit_category], many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_audit_categories_view_with_invalid_audit_type(self):
        response = self.client.get('/audit/audit-categories/1101')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostAuditDataViewTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

        self.db_client = MongoClient(
            'mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        self.db = self.db_client['masys']
        self.collection = self.db['audit_data']

        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        self.temp_file.close()
        time.sleep(0.1)
        os.unlink(self.temp_file.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_audit_data(self):
        # Create a zip file with some test data
        workbook = Workbook()
        worksheet = workbook.create_sheet("Sheet1")
        worksheet.append(['Name', 'Age'])
        worksheet.append(['Alice', 25])
        worksheet.append(['Bob', 30])
        file_data = io.BytesIO()
        workbook.save(file_data)
        file_data.seek(0)
        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, 'w') as zip_file:
            zip_file.writestr('example.xlsx', file_data.getvalue())
        zip_data.seek(0)

        response = self.client.post('/audit/upload-data',
                                    {'file': zip_data, 'audit_session_id': 1001}, format='multipart')

        # Check the response has a success status code and the expected message and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'File uploaded to database', 'data': 'audit-data-1001'})

        # Check that the files were saved to the child collection
        data_name = 'audit-data-1001'
        child_collection = self.collection[data_name]
        self.assertEqual(child_collection.count_documents({}), 2)

        # Reset test data on database
        child_collection.delete_many({})


class GetAuditQuestionsViewTestCase(unittest.TestCase):
    def setUp(self):
        self.audit_type = AuditType.objects.create(label='Some Audit Type')
        self.audit_category = AuditCategory.objects.create(title='Some Audit Category', audit_type=self.audit_type)
        self.audit_question = AuditQuestion.objects.create(title='Some Audit Question',
                                                           audit_category=self.audit_category)

        self.client = APIClient()
        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

    def test_get_audit_questions_view(self):
        response = self.client.get('/audit/audit-questions/'+str(self.audit_category.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = AuditQuestionSerializer([self.audit_question], many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_audit_questions_view_with_invalid_audit_category(self):
        response = self.client.get('/audit/audit-questions/123456789')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
