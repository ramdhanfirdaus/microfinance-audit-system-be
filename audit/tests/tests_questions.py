from rest_framework.test import APIClient
from rest_framework import status

from django.test import override_settings

from pymongo import MongoClient

from requests_toolbelt.multipart.encoder import MultipartEncoder

import unittest, tempfile, pytest, json

from audit.views.views_questions import save_attachment, save_comment_remark, query_sample
from audit.test_utils import cek_mongodb, create_test_zip, delete_audit_question_session, login_test, test_post_audit_data


class QueryQuestionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        db = client['masys']
        collection = db['audit_data']
        collection.insert_one({'name': 'audit-data-123'})

        test_post_audit_data(self.client)

    def tearDown(self):
        delete_audit_question_session('audit_data', 'audit-data', '123')

    def test_query_sample_with_valid_input(self):
        id_session = "123"
        query = {'Name': 'Alice'}
        sort = [("Age", 1)]
        limit = 0

        result = query_sample(id_session, query, sort, limit)
        result_list = json.loads(result)

        self.assertEqual(result_list[0]["Name"], 'Alice')

    def test_query_sample_with_invalid_session_id(self):
        id_session = "456"
        query = {'Name': 'John'}
        sort = [("Age", 1)]
        limit = 0
        with pytest.raises(ValueError):
            query_sample(id_session, query, sort, limit)

    def test_query_sample_with_empty_session_id(self):
        id_session = None
        query = {'Name': 'John'}
        sort = [("Age", 1)]
        limit = 0
        with pytest.raises(ValueError):
            query_sample(id_session, query, sort, limit)


class PostAuditQuestionSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.temp_file = create_test_zip()

    def tearDown(self):
        self.temp_file.close()
        delete_audit_question_session('attachment', 'attachment', 'test')

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