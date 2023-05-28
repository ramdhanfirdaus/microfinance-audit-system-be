from rest_framework.test import APIClient
from rest_framework import status

import unittest
from .apps import MyappConfig

from django.apps import apps


class MyAppTestCase(unittest.TestCase):
    def test_apps(self):
        self.assertEqual(MyappConfig.name, "myapp")
        self.assertEqual(apps.get_app_config("myapp").name, "myapp")

class HomeAdminTestCase(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_home_admin(self):
        response = self.client.get('')
        assert response.status_code == status.HTTP_302_FOUND