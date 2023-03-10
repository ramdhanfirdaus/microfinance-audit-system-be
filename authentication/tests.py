from django.test import TestCase
import unittest
import requests
from .views import *

# Create your tests here.


class LoginTest(unittest.TestCase):
    def test_success_login_can_access_views_with_authentication(self):
        # Gather token
        url = 'http://localhost:8000/authentication/token/'
        r = requests.post(
            url, json={"username": "naruto", "password": "naruto"})
        tokens = r.json()

        # Check whether login is successful
        url = 'http://localhost:8000/authentication/hasloggedin/'
        r = requests.get(
            url, header={"Authorization": f"Bearer {tokens['access']}"})
        status = r.json()

        self.assertDictEqual(status, {{"Logged-In": 1}})

    def test_anonymous_user_cannot_accesss_views_with_authentication(self):
        pass
