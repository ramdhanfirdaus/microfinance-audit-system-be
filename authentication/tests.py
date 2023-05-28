from rest_framework.test import APIClient
from rest_framework import status
import unittest

from .models import Auditor
from .apps import AuthenticationConfig
from audit.test_utils import login_test

from django.apps import apps
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.hashers import make_password
import json


class AuthenticationAppTestCase(unittest.TestCase):
    def test_apps(self):
        self.assertEqual(AuthenticationConfig.name, "authentication")
        self.assertEqual(apps.get_app_config("authentication").name, "authentication")


class RegisterApiTestView(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def register(self, token, data):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.post("/authentication/register/", data)

    def test_register(self):
        tokens = login_test()
        data = {
            "username": "usertest",
            "password": "password",
            "first_name": "usertest",
            "last_name": "usertest",
            "email": "user@test.com",
        }

        response = self.register(tokens["access"], data)

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(username="usertest")
        Auditor.objects.get(user=user).delete()
        user.delete()

    def test_register_failed_invalid_email(self):
        tokens = login_test()
        data = {
            "username": "usertest",
            "password": "usertest",
            "first_name": "usertest",
            "last_name": "usertest",
            "email": "user@testcom",
        }

        response = self.register(tokens["access"], data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Enter a valid email address.' in response.json()['email'])
        
        self.assertFalse(User.objects.filter(username="usertest").exists())

    def test_register_failed_invalid_username(self):
        tokens = login_test()
        data = {
            "username": "us",
            "password": "usertest",
            "first_name": "usertest",
            "last_name": "usertest",
            "email": "user@testcom",
        }

        response = self.register(tokens["access"], data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Ensure this value has at least 3 characters (it has 2).' in response.json()['username'])

        self.assertFalse(User.objects.filter(username="usertest").exists())

    def test_register_failed_username_password_same(self):
        tokens = login_test()
        data = {
            "username": "usertest",
            "password": "usertest",
            "first_name": "usertest",
            "last_name": "usertest",
            "email": "user@test.com",
        }

        response = self.register(tokens["access"], data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Username and password should not be the same.' in response.json()['non_field_errors'])

        self.assertFalse(User.objects.filter(username="usertest").exists())


class RegisterApiTestView(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

    def register(self, token, data):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        return self.client.post("/authentication/register/", data)

    def test_register(self):
        tokens = login_test()
        data = {
            "username": "usertest",
            "password": "usertest",
            "first_name": "usertest",
            "last_name": "usertest",
        }

        response = self.register(tokens["access"], data)

        # Check that the response has a 200 OK status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get(username="usertest")
        Auditor.objects.get(user=user).delete()
        user.delete()

class AuditorTest(unittest.TestCase):
    def test_auditor_class_has_all_needed_attribute(self):
        # self.assertTrue(hasattr(Auditor(), 'user'))
        self.assertTrue(hasattr(Auditor(), "on_audit"))
        self.assertTrue(hasattr(Auditor(), "session"))  # R


class DeleteAuditorTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()

        User.objects.update_or_create(id=-1)

        Auditor.objects.update_or_create(id=-1, user=User.objects.get(id=-1))

        self.login_url = "/authentication/token/"

        self.admin_auth_response = self.client.post(
            self.login_url, {"username": "naruto", "password": "naruto"}
        )
        self.admin_tokens = self.admin_auth_response.json()

        self.auditor_auth_response = self.client.post(
            self.login_url, {"username": "sasuke", "password": "sasuke"}
        )
        self.auditor_tokens = self.auditor_auth_response.json()

    def delete_auditor(self, token, id_auditor):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.delete(f"/authentication/delete-auditor/{id_auditor}")

    def test_delete_auditor_not_login(self):
        response = self.delete_auditor("token", 1)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_auditor_not_admin(self):
        response = self.delete_auditor(self.auditor_tokens["access"], 1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_auditor_not_found(self):
        response = self.delete_auditor(self.admin_tokens["access"], -2)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_auditor_success(self):
        self.assertTrue(User.objects.filter(id=-1).exists())
        self.assertTrue(Auditor.objects.filter(id=-1).exists())
        response = self.delete_auditor(self.admin_tokens["access"], -1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["success"], True)
        self.assertFalse(User.objects.filter(id=-1).exists())
        self.assertFalse(Auditor.objects.filter(id=-1).exists())


class GetAuditorIdByUserIdTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.get(username="naruto")
        self.user = User.objects.get(username="testuser")

    def test_get_auditor_id_by_user_id_not_auditor(self):
        url = reverse("get_auditor_by_user_id", args=[self.admin.id])
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"auditor_id": None})

    def test_get_auditor_id_by_user_id(self):
        self.auditor = Auditor.objects.get(user=self.user)
        url = reverse("get_auditor_by_user_id", args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"auditor_id": self.auditor.id})


class ChangePasswordTest(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="usernamechangepwtest", password=make_password("pwchangepwtest")
        )
        self.valid_request_data = {
            "id_user": self.user.id,
            "current_password": "pwchangepwtest",
            "new_password": "newpwchangepwtest",
            "confirm_password": "newpwchangepwtest",
        }
        self.mismatch_request_data = {
            "id_user": self.user.id,
            "current_password": "pwchangepwtest",
            "new_password": "newpwchangepwtest",
            "confirm_password": "wrongnewpwchangepwtest",
        }
        self.wrong_request_data = {
            "id_user": self.user.id,
            "current_password": "wrongpwchangepwtest",
            "new_password": "newpwchangepwtest",
            "confirm_password": "newpwchangepwtest",
        }
        self.another_valid_request_data = {
            "id_user": self.user.id,
            "current_password": "pwchangepwtest",
            "new_password": "newpwchangepwtest",
            "confirm_password": "newpwchangepwtest",
        }
        self.login_url = "/authentication/token/"
        self.auth_response = self.client.post(
            self.login_url,
            {"username": "usernamechangepwtest", "password": "pwchangepwtest"},
        )
        self.tokens = self.auth_response.json()

    def tearDown(self):
        self.user.delete()

    def change_password(self, token, data):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return self.client.post("/authentication/change-password/", data=data)

    def test_change_password_not_login(self):
        response = self.change_password("token", self.another_valid_request_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_mismatch(self):
        response = self.change_password(
            self.tokens["access"], self.mismatch_request_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), "New password dan confirm password berbeda!")
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(self.valid_request_data["current_password"])
        )

    def test_change_password_wrong_current(self):
        response = self.change_password(self.tokens["access"], self.wrong_request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), "Password saat ini salah!")
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(self.valid_request_data["current_password"])
        )

    def test_change_password_success(self):
        response = self.change_password(self.tokens["access"], self.valid_request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), "Password berhasil diubah.")
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(self.valid_request_data["new_password"])
        )
