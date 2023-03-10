from django.test import TestCase
import unittest
from .views import hello

# Create your tests here.


class LoginTest(unittest.TestCase):
    def test_log_in_is_successful(self):
