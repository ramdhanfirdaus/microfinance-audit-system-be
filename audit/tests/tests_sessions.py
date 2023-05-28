import unittest

from rest_framework.test import APIClient
from rest_framework import status

from audit.test_utils import login_test, create_test_objects, delete_test_objects, make_auditors_test, delete_auditors_test
from authentication.models import Auditor
from audit.views.views_sessions import cek_auditors, set_auditor_history
from audit.models import AuditSession, AuditHistory


class GetAuditorsBySessionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        create_test_objects()
        make_auditors_test()

    def tearDown(self):
        delete_test_objects()
        delete_auditors_test()

    def get_auditors_by_session(self, token, id_session, user_id):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.get('/audit/get-auditor-by-session/' + id_session + '/' + user_id)

    def test_get_auditors_by_session_not_login(self):
        response = self.get_auditors_by_session("token", "123", "123")

        # Check that the response has a 401 UNAUTHORIZED status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_auditors_by_session_on_completed_session(self):
        tokens = login_test()
        response = self.get_auditors_by_session(tokens['access'], "456", "123")

        # Check that the response has a 404 NOT FOUND status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_auditors_by_session_on_empty_session(self):
        tokens = login_test()
        response = self.get_auditors_by_session(tokens['access'], "789", "123")

        # Check that the response has a 404 NOT FOUND status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_auditors_by_session_with_equals_id(self):
        tokens = login_test()
        response = self.get_auditors_by_session(tokens['access'], "123", "123")

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_auditors_by_session_without_equals_id(self):
        tokens = login_test()
        response = self.get_auditors_by_session(tokens['access'], "123", "789")

        # Check that the response has a 403 FORBIDDEN status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CekAuditorsTestCase(unittest.TestCase):
    def setUp(self):
        create_test_objects()
        self.auditors = make_auditors_test()

    def tearDown(self):
        delete_test_objects()
        delete_auditors_test()

    def test_cek_auditors_with_equals_id(self):
        flag, lst_name, lst_id = cek_auditors(123, self.auditors)

        self.assertEqual(flag, True)
        self.assertEqual(lst_name, "testing 1, testing 2")
        self.assertEqual(lst_id, [123, 456])

    def test_cek_auditors_without_equals_id(self):
        flag, lst_name, lst_id = cek_auditors(789, self.auditors)

        self.assertEqual(flag, False)
        self.assertEqual(lst_name, "testing 1, testing 2")
        self.assertEqual(lst_id, [123, 456])


class GetSessionByAuditorTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        create_test_objects()
        make_auditors_test()

        self.auditor = Auditor.objects.get(id=123)

    def tearDown(self):
        delete_test_objects()
        delete_auditors_test()

    def get_session_by_auditor(self, token, user_id):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.get('/audit/get-session-by-auditor/' + user_id)

    def test_get_session_by_auditor_not_login(self):
        response = self.get_session_by_auditor("token", "123")

        # Check that the response has a 401 UNAUTHORIZED status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_session_by_auditor_on_empty_session(self):
        tokens = login_test()
        response = self.get_session_by_auditor(tokens['access'], "789")

        data = {
            'message': 'Anda tidak memiliki sesi audit aktif.'
        }

        # Check that the response has a 404 NOT FOUND status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response data
        self.assertEqual(response.json(), data)

    def test_get_session_by_auditor_with_equals_id(self):
        tokens = login_test()
        response = self.get_session_by_auditor(tokens['access'], "123")

        data = {
            'id_session': self.auditor.session.id
        }

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response data
        self.assertEqual(response.json(), data)


class StopAuditTestCase(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        create_test_objects()
        make_auditors_test()

        self.active_session = AuditSession.objects.get(id=123)
        self.inactive_session = AuditSession.objects.get(id=999)

    def tearDown(self):
        delete_test_objects()
        delete_auditors_test()

    def stop_audit(self, token, id_session, ids_auditor):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {
            "idSession": id_session,
            "idsAuditor": ids_auditor
        }

        return self.client.post('/audit/stop-audit', data)

    def test_stop_audit_not_login(self):
        response = self.stop_audit("token", "123", "123")

        # Check that the response has a 401 UNAUTHORIZED status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stop_audit_on_completed_session(self):
        tokens = login_test()
        response = self.stop_audit(tokens['access'], self.inactive_session.id, [0])

        # Check that the response has a 403 FORBIDDEN status code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stop_audit_on_incompleted_session(self):
        tokens = login_test()
        response = self.stop_audit(tokens['access'], self.active_session.id, [0])

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SetAuditorHistoryTestCase(unittest.TestCase):
    def setUp(self):
        create_test_objects()
        make_auditors_test()

        self.active_session = AuditSession.objects.get(id=123)
        self.history = AuditHistory.objects.create(id=999, audit_session=self.active_session)

    def tearDown(self):
        delete_test_objects()
        delete_auditors_test()
        self.history.delete()

    def test_set_auditor_history(self):
        set_auditor_history([123, 789], self.history)

        self.assertEqual("[123, 789]", self.history.list_auditor)
        self.assertEqual("['testing 1', 'testing 3']", self.history.auditors_name)
