import unittest
from rest_framework import status
from rest_framework.test import APIClient

from audit.models import AuditType

class PostAuditTypeTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        self.login_url = '/authentication/token/'
        self.auth_response = self.client.post(self.login_url, {"username": "naruto", "password": "naruto"})
        self.tokens = self.auth_response.json()

        self.audit_type_data_1 = {
            'label': 'Test Audit Type 1'
        }

        self.audit_type_data_2 = {
            'label': 'Test Audit Type 2'
        }

        self.audit_type_missing_data = {
            'title': 'Test Audit Type'
        }

    def tearDown(self):
        self.delete_object_type(self.audit_type_data_1['label'].lower())
        self.delete_object_type(self.audit_type_data_2['label'].lower())

    def delete_object_type(self, label):
        try:
            AuditType.objects.get(label=label).delete()
        except Exception:
            pass

    def post_audit_type(self, token, audit_type):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.post('/audit/create-audit-type', data=audit_type)

    def test_post_audit_type_not_login(self):
        response = self.post_audit_type('token', self.audit_type_data_1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_audit_type_success(self):
        response = self.post_audit_type(self.tokens['access'], self.audit_type_data_1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['success'], True)

        response = self.post_audit_type(self.tokens['access'], self.audit_type_data_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['success'], True)

    def test_post_audit_type_missing_parameter(self):
        response = self.post_audit_type(self.tokens['access'], self.audit_type_missing_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Missing required parameters')

    def test_post_audit_type_duplicate_label(self):
        self.post_audit_type(self.tokens['access'], self.audit_type_data_1)
        response = self.post_audit_type(self.tokens['access'], self.audit_type_data_1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Sudah ada kategori dengan nama yang sama')
