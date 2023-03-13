from django.test import TestCase
import unittest
import requests
from .models import *
from .views import *


# Create your tests here.
class AuditorTest(unittest.TestCase):
    def test_auditor_class_has_all_needed_attribute(self):
        self.assertTrue(hasattr(Auditor(), 'user'))
        self.assertTrue(hasattr(Auditor(), 'on_audit'))


class LoginTest(unittest.TestCase):
    # TODO make this test to execute only when test instance is running
    def test_success_login_can_access_views_with_authentication(self):
        # Gather token
        url = 'http://localhost:8000/authentication/token/'
        r = requests.post(
            url, json={"username": "naruto", "password": "naruto"})
        tokens = r.json()

        # Check whether login is successful
        url = 'http://localhost:8000/authentication/hasloggedin/'
        r = requests.get(
            url, headers={"Authorization": f"Bearer {tokens['access']}"})
        status = r.json()

        self.assertDictEqual(status, {"Logged-In": 1})

    def test_anonymous_user_cannot_accesss_views_with_authentication(self):
        # Check whether login is successful
        url = 'http://localhost:8000/authentication/hasloggedin/'
        r = requests.get(url)
        status = r.json()

        self.assertDictEqual(
            status, {'detail': 'Authentication credentials were not provided.'})

    def test_logged_in_user_data_views_returns_user_data(self):
        # Gather token
        url = 'http://localhost:8000/authentication/token/'
        r = requests.post(
            url, json={"username": "naruto", "password": "naruto"})
        tokens = r.json()

        # Check whether login is successful
        url = 'http://localhost:8000/authentication/hasloggedin/'
        r = requests.get(
            url, headers={"Authorization": f"Bearer {tokens['access']}"})
        data = r.json()

        self.assertDictEqual(data, {"username": "naruto"})
