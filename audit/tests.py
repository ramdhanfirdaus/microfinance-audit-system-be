from rest_framework.test import APIClient
from rest_framework import status

from django.test import override_settings
from django.apps import apps

from pymongo import MongoClient
from openpyxl import Workbook

from requests_toolbelt.multipart.encoder import MultipartEncoder

import unittest, os, tempfile, zipfile, io

from openpyxl import Workbook

from .apps import AuditConfig
from .models import AuditQuestion, AuditType, AuditSession, AuditCategory
from .serializer import AuditQuestionSerializer, AuditTypeSerializer, AuditSessionSerializer, AuditCategorySerializer
from .views_questions import save_attachment, save_comment_remark
from .test_utils import cek_mongodb, create_test_zip, delete_audit_question_session, login_test


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
        response = self.client.put('/audit/create-new-audit-session/'+type_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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

        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

        
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
        self.url = '/audit/upload-data'
        
        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

        self.db_client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        self.db = self.db_client['masys']
        self.collection = self.db['audit_data']

        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file = 'test_file.txt'
        self.test_zip = 'test_file.zip'

    def tearDown(self):
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

        with open(self.test_file, 'w') as f:
            f.write('This is a test file')

        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, 'w') as zip_file:
            zip_file.writestr('example.xlsx', file_data.getvalue())
            zip_file.write(self.test_file)
        zip_data.seek(0)

        response = self.client.post(self.url, 
                                    {'file': zip_data, 'audit_session_id' : 1001}, format='multipart')

        # Check the response has a success status code and the expected message and data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'File uploaded to database', 'data': 'audit-data-1001'})

        # Check that the files were saved to the child collection
        data_name = 'audit-data-1001'
        child_collection = self.collection[data_name]
        self.assertEqual(child_collection.count_documents({}), 2)

        # Reset test data on database
        child_collection.delete_many({})
        child_collection.drop()

        os.remove(self.test_file)

    def test_upload_invalid_file(self):
        # create a fake zip file
        with open(self.test_file, 'w') as f:
            f.write('This is a fail test file')

        with zipfile.ZipFile(self.test_zip, 'w') as myzip:
             myzip.write(self.test_file)

        # create a request with the fake zip file
        with open(self.test_zip, 'rb') as file:
            data = {'file': file, 'audit_session_id': 1001}
            response = self.client.post(self.url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Invalid zip file')

        # delete the test files
        os.remove(self.test_zip)
        os.remove(self.test_file)
        

class PostAuditQuestionSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.temp_file = create_test_zip()

    def tearDown(self):
        self.temp_file.close()
        delete_audit_question_session('attachment', 'test')

    def post_audit_question_session(self, token):
        with open(self.temp_file.name, 'rb') as f:
            multipart_data = MultipartEncoder(fields={
                'id_audit': 'test',
                'comment': 'test',
                'remark': 'test',
                'attachment': ('filename.zip', f, 'application/zip')
            })

            data_dict = {k: v[1] if isinstance(v, tuple) else v for k, v in multipart_data.fields.items()}

            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

            return self.client.post('/audit/audit-question-session', data=data_dict, format='multipart')

    def test_post_url_audit_question_session_not_login(self):
        response = self.post_audit_question_session("token")

        # Check that the response has a 401 UNAUTHORIZED status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_post_url_audit_question_session(self):
        tokens = login_test()

        collections_count, child_collections_count = cek_mongodb('attachment', 'test')
        self.assertEqual(collections_count, 0)
        self.assertEqual(child_collections_count, 0)

        # Post in First Time addition collections_count and child_collections_count
        response = self.post_audit_question_session(tokens['access'])

        collections_count, child_collections_count = cek_mongodb('attachment', 'test')
        self.assertEqual(collections_count, 1)
        self.assertEqual(child_collections_count, 1)

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Post in Second Time just addition child_collections_count
        response = self.post_audit_question_session(tokens['access'])

        collections_count, child_collections_count = cek_mongodb('attachment', 'test')
        self.assertEqual(collections_count, 1)
        self.assertEqual(child_collections_count, 2)

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SaveAttachmentTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file = create_test_zip()

    def tearDown(self):
        self.temp_file.close()

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_save_attachment(self):
        with open(self.temp_file.name, 'rb') as attachment:
            data = {}
            data = save_attachment(attachment, data)
            self.assertNotEqual(data, {})


class SaveCommentRemarkTestCase(unittest.TestCase):
    def test_save_comment_remark(self):
        data = {}
        comment = 'Test comment'
        remark = 'Test remark'
        data = save_comment_remark(comment, remark, data)
        self.assertIn('comment', data.keys())
        self.assertIn('remark', data.keys())
        self.assertEqual(data['comment'], comment)
        self.assertEqual(data['remark'], remark)


class GetAuditQuestionsViewTestCase(unittest.TestCase):
    def setUp(self):
        self.audit_type = AuditType.objects.create(label='Some Audit Type')
        self.audit_category = AuditCategory.objects.create(title='Some Audit Category', audit_type=self.audit_type)
        self.audit_question = AuditQuestion.objects.create(title='Some Audit Question', audit_category=self.audit_category)

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
