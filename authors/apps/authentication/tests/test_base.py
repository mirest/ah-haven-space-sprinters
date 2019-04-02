import json
from django.core import mail
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
            } 
        }
        
        self.update_user = {
            "user": {
                "username": "update",

            }
        }

        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username='testinguser',
            email='testemail@test.com', password='Test1ngwork')
        self.verified_user_login_credentials = {
            "user": {
                "email": "testemail@test.com",
                "password": "Test1ngwork"
            }
        }

        self.profile_data = {
            "first_name": "Keira",
            "last_name": "Knightly",
            "bio": "Actress, model, female"
        }

    def auth_header_token(self):
        self.client.post(
            reverse('auth:register'),
            data=self.user_data,
            format='json')
        self.login_credentials={
            "user": {
                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
            }
        }

        response = self.client.post(
            reverse('auth:login'),
            data=self.login_credentials,
            format='json')

        self.test_token = response.data.get("auth_token")
        self.auth_header = 'Bearer {}'.format(self.test_token)

        return self.auth_header

    def verified_user_login_token(self):
        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')

        response = self.client.post(
            reverse('auth:login'),
            data=self.user_data,
            format='json')

        self.test_user_token = response.data.get("auth_token")
        self.valid_auth_token = 'Bearer {}'.format(self.test_user_token)
        
        return self.valid_auth_token
