import unittest
from rest_framework import status
from rest_framework.test import APIClient
from audit.models import AuditCategory, AuditType, AuditSession
from audit.test_utils import login_test
from audit.serializer import AuditCategorySerializer

class PostAuditCategoryTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        AuditType.objects.update_or_create(
            id=123
        )

        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.audit_category_1_data = {
            'title': 'Test Audit Category 1',
            'audit_type_id': 123
        }
        self.audit_category_2_data = {
            'title': 'Test Audit Category 2',
            'audit_type_id': 123
        }
        self.audit_category_missing_data = {
            'title': 'Test Audit Missing'
        }

    def tearDown(self):
        AuditType.objects.get(id=123).delete()

    def post_audit_category(self, token, audit_category):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.post('/audit/create-audit-category', data=audit_category)

    def test_post_audit_category_not_login(self):
        response = self.post_audit_category('token', self.audit_category_1_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_audit_category_success(self):
        response = self.post_audit_category(self.tokens['access'], self.audit_category_1_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['success'], True)

        response = self.post_audit_category(self.tokens['access'], self.audit_category_2_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['success'], True)

    def test_post_audit_category_missing_parameter(self):
        response = self.post_audit_category(self.tokens['access'], self.audit_category_missing_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Missing required parameters')

    def test_post_audit_category_duplicate_title(self):
        self.post_audit_category(self.tokens['access'], self.audit_category_1_data)
        response = self.post_audit_category(self.tokens['access'], self.audit_category_1_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Sudah ada kategori dengan nama yang sama')

class GetAllAuditCategoriesTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

    def tearDown(self) -> None:
        return super().tearDown()

    def get_all_audit_category(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.get('/audit/get-all-audit-categories/')

    def test_get_all_audit_category_not_login(self):
        response = self.get_all_audit_category('token')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_all_audit_category_success(self):
        response = self.get_all_audit_category(self.tokens['access'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        count = AuditCategory.objects.count()
        response_count = len(response.json())
        self.assertEqual(count, response_count)


class GetAuditCategoriesBySessionTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tokens = login_test()

        self.audit_type_1 = AuditType.objects.create(label='Some Audit Type 1')
        self.audit_session_1 = AuditSession.objects.create(type=self.audit_type_1)
        self.audit_category_1 = AuditCategory.objects.create(title='Some Audit Category 1', audit_type=self.audit_type_1)

        self.audit_type_2 = AuditType.objects.create(label='Some Audit Type 2')
        self.audit_session_2 = AuditSession.objects.create(type=self.audit_type_2)

    def tearDown(self) -> None:
        self.audit_type_1.delete()
        self.audit_session_1.delete()
        self.audit_category_1.delete()
        self.audit_type_2.delete()
        self.audit_session_2.delete()
        return super().tearDown()

    def get_audit_categories_by_session(self, token, id):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.get('/audit/audit-categories-by-session/' + str(id))

    def test_get_audit_categories_by_session_not_login(self):
        response = self.get_audit_categories_by_session('token', -1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_audit_categories_by_session_view(self):
        response = self.get_audit_categories_by_session(self.tokens['access'], self.audit_session_1.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data = AuditCategorySerializer([self.audit_category_1], many=True).data
        self.assertEqual(response.data, serializer_data)

    def test_get_audit_categories_by_session_view_with_invalid_audit_session(self):
        response = self.get_audit_categories_by_session(self.tokens['access'], self.audit_session_2.id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)