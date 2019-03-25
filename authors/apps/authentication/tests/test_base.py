from django.test import TestCase
from authors.apps.authentication.models import User
from rest_framework.test import APIClient


class BaseTestClass(TestCase):
    def setUp(self):
        self.user_data = {
            "user": {
                "username": "sampleuser",
                "email": "user@sprinters.ug",
                "password": "butt3rfly1"
            }
        }

        self.invalid_user = {
            "user": {
                "email": "hacker@someplace.cc",
                "password": "123passsing"

            }
        }

        self.client = APIClient()