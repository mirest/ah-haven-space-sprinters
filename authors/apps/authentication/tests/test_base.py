from django.test import TestCase
from authors.apps.authentication.models import User
from rest_framework.test import APIClient
from django.urls import reverse


class BaseTestClass(TestCase):
    def setUp(self):
        self.user_data = {
            "user": {
                "username": "sampleuser",
                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
            }
        }

        self.invalid_user = {
            "user": {
                "email": "hacker@someplace.cc",
                "password": "123passsing"

            }
        }
        self.same_email_user = {
            "user": {
                "username": "samuel",
                "email": "user@sprinters.ug",
                "password": "Samm1eboy"
            }
        }

        self.same_username_user = {
            "user": {
                "username": "sampleuser",
                "email": "samuel@gmail.com",
                "password": "Robb1ezon"
         } }

        self.invalid_username = {
            "user": {
                "username": "min#*r",
                "email": "minnie@gmail.com",
                "password": "Robb1ezon"
         } }


        self.update_user = {
            "user": {
                "username": "update",

            }
        }

        self.reset_user_password = {
            'user': {
                'username': 'sprintersspace',
                'password': 'sprintersspacePassword',
                'email': 'sprintersspace@gmail.com'
            }
        }

        self.client = APIClient()

    def auth_header_token(self):
        self.client.post(
            reverse('auth:register'),
            data=self.user_data,
            format='json')

        response = self.client.post(
            reverse('auth:login'),
            data=self.user_data,
            format='json')

        self.test_token = response.data.get("auth_token")
        self.auth_header = 'Bearer {}'.format(self.test_token)

        return self.auth_header