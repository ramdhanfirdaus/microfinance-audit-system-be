from datetime import datetime, timedelta

from rest_framework.test import APIClient
from rest_framework import status

from django.test import override_settings
from unittest.mock import patch

from pymongo import MongoClient

import tempfile, zipfile, configparser

from requests_toolbelt.multipart.encoder import MultipartEncoder

import unittest, tempfile, pytest, json

from audit.models import (
    AuditSession,
    AuditQuestion,
    AuditCategory,
    AuditType,
    AuditHistory,
)
from audit.test_utils import login_test

from authentication.models import Auditor, User
from audit.views.views_history import get_history
from audit.dto.pdf_dto import PdfDTO 


class GetHistoryTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def get_audit_history(self, username, password):
        response = self.client.post(
            "/authentication/token/", data={"username": username, "password": password}
        )
        response = response.json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response['access']}")
        return self.client.get("/audit/history")

    def test_get_user_history_not_logged_in(self):
        response = self.client.get("/audit/history")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_history_success(self):
        response = self.get_audit_history("sasuke", "sasuke")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_history_failed_not_by_auditor(self):
        response = self.get_audit_history("naruto", "naruto")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetResultHTMLTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        DB = MongoClient(
            "mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true"
        )[config.get('credentials', 'database')]
        AuditHistory.objects.update_or_create(id=123)

    def tearDown(self):
        AuditHistory.objects.get(id=123).delete()

    def get_html_result(self, token, history_id):
        data = {'history_id': history_id}

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.post('/audit/get-result-html', data=data)

    @patch('audit.dto.pdf_dto.PdfDTO.__init__')
    def test_get_result_html_success(self, mock_pdf_dto_init):
        mock_pdf_dto_init.return_value = None

        tokens = login_test()

        response = self.get_html_result(tokens['access'], 123)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('audit.dto.pdf_dto.PdfDTO.__init__')
    def test_get_result_html_failed(self, mock_pdf_dto_init):
        mock_pdf_dto_init.return_value = None

        tokens = login_test()

        response = self.get_html_result(tokens['access'], 321)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

class DownloadResultPDFTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        DB = MongoClient(
            "mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true"
        )[config.get('credentials', 'database')]
        AuditHistory.objects.update_or_create(id=123)

    def tearDown(self):
        AuditHistory.objects.get(id=123).delete()

    def download_result_pdf(self, token, history_id):
        data = {'history_id': history_id}

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.post('/audit/download-report-file', data=data)

    @patch('audit.dto.pdf_dto.PdfDTO.__init__')
    def test_get_result_html_success(self, mock_pdf_dto_init):
        mock_pdf_dto_init.return_value = None

        tokens = login_test()

        response = self.download_result_pdf(tokens['access'], 123)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue('Content-Disposition' in response)

    @patch('audit.dto.pdf_dto.PdfDTO.__init__')
    def test_get_result_html_failed(self, mock_pdf_dto_init):
        mock_pdf_dto_init.return_value = None

        tokens = login_test()

        response = self.download_result_pdf(tokens['access'], 321)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
