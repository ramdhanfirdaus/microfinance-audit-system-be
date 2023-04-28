from datetime import datetime, timedelta

from rest_framework.test import APIClient
from rest_framework import status

from django.test import override_settings

from pymongo import MongoClient

from requests_toolbelt.multipart.encoder import MultipartEncoder

import unittest, tempfile, pytest, json

from audit.models import AuditSession
from audit.views.views_questions import save_attachment, save_comment_remark, query_sample, manage_query, query_date, json_converter
from audit.test_utils import cek_mongodb, create_test_zip, delete_audit_question_session, login_test, test_post_audit_data, \
   create_test_objects, delete_test_objects


class GetSampleTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        create_test_objects()

        client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        db = client['coba']
        collection = db['audit_data']
        collection.insert_one({'name': 'audit-data-123'})

    def tearDown(self):
        delete_audit_question_session('audit_data', 'audit-data', '123')
        delete_test_objects()

    def get_sample(self, token, id_session, id_question):
        data = {
            'id_session': id_session,
            'id_question': id_question
        }

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.get('/audit/sample-data', data=data)

    def test_get_sample_not_login(self):
        response = self.get_sample("token", "123", "123")

        # Check that the response has a 401 UNAUTHORIZED status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_sample_not_have_data(self):
        test_post_audit_data(self.client)

        tokens = login_test()
        response = self.get_sample(tokens['access'], "456", "456")

        # Check that the response has a 404 NOT FOUND status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_get_sample_not_have_query(self):
        test_post_audit_data(self.client)

        tokens = login_test()
        response = self.get_sample(tokens['access'], "456", "789")

        # Check that the response has a 404 NOT FOUND status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_sample_have_data(self):
        test_post_audit_data(self.client)

        tokens = login_test()
        response = self.get_sample(tokens['access'], "123", "123")

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ManageQueryTestCase(unittest.TestCase):
    def setUp(self):
        create_test_objects()
        self.session = AuditSession.objects.get(id=123)

    def tearDown(self):
        delete_audit_question_session('audit_data', 'audit-data', '123')
        delete_test_objects()

    def test_manage_query_with_sort_limit(self):
        query_str = '''
          {
             "Name": "Alice",
             "sort": [["Age", 1]],
             "limit": 1
          }
          '''

        query, limit, sort = manage_query(query_str, self.session.date)

        self.assertEqual(limit, [("Age", 1)])
        self.assertEqual(sort, 1)

    def test_manage_query_without_sort_limit(self):
        query_str = '{"Name": "Alice"}'

        query, limit, sort = manage_query(query_str, self.session.date)

        self.assertEqual(limit, {})
        self.assertEqual(sort, 0)

    def test_manage_query_with_tgl_kondisi(self):
        query_str = '{"Name": "John", "TGL_KONDISI": {"$gte": "LASTMONTH", "$lte": "TODAY"}}'

        query, limit, sort = manage_query(query_str, self.session.date)

        self.assertIn('TGL_KONDISI', query)
        self.assertIn('$gte', query['TGL_KONDISI'])
        self.assertIn('$lte', query['TGL_KONDISI'])

        self.assertNotEqual(query['TGL_KONDISI']['$gte'], "LASTMONTH")
        self.assertNotEqual(query['TGL_KONDISI']['$lte'], "TODAY")

    def test_manage_query_without_tgl_kondisi(self):
        query_str = '{"Name": "Alice"}'
        expected_result = {'Name': 'Alice'}

        query, limit, sort = manage_query(query_str, self.session.date)

        self.assertEqual(query, expected_result)


class JsonConverterTestCase(unittest.TestCase):
    def test_datetime_conversion(self):
        test_datetime = datetime(2022, 1, 1, 10, 30, 0)
        result = json.dumps(test_datetime, default=json_converter)
        self.assertEqual(result, '"2022-01-01 10:30:00"')

    def test_invalid_object_type(self):
        test_object = {1, 2, 3}
        with self.assertRaises(TypeError):
          json.dumps(test_object, default=json_converter)


class QueryDateTestCase(unittest.TestCase):
    def setUp(self):
        create_test_objects()
        self.session = AuditSession.objects.get(id=123)

    def tearDown(self):
        delete_audit_question_session('audit_data', 'audit-data', '123')
        delete_test_objects()

    def test_query_date_with_last_year(self):
        query = {"TGL_KONDISI": {"$gte": "LASTYEAR"}}
        params = ["TGL_KONDISI", "$gte"]
        query = query_date(query, self.session.date, params)

        expected_date = self.session.date - timedelta(days=365)

        self.assertLessEqual(query['TGL_KONDISI']['$gte'], expected_date)

    def test_query_date_with_last_month(self):
        query = {"TGL_KONDISI": {"$gte": "LASTMONTH"}}
        params = ["TGL_KONDISI", "$gte"]
        query = query_date(query, self.session.date, params)

        expected_date = self.session.date - timedelta(days=30)

        self.assertEqual(query["TGL_KONDISI"]["$gte"], expected_date)

    def test_query_date_with_yesterday(self):
        query = {"TGL_KONDISI": {"$gte": "YESTERDAY"}}
        params = ["TGL_KONDISI", "$gte"]
        query = query_date(query, self.session.date, params)

        expected_date = self.session.date - timedelta(days=1)

        self.assertEqual(query["TGL_KONDISI"]["$gte"], expected_date)

    def test_query_date_with_today(self):
        query = {"TGL_KONDISI": {"$lte": "TODAY"}}
        params = ["TGL_KONDISI", "$lte"]
        query = query_date(query, self.session.date, params)

        expected_date = self.session.date

        self.assertEqual(query["TGL_KONDISI"]["$lte"], expected_date)


class QueryQuestionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        db = client['coba']
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