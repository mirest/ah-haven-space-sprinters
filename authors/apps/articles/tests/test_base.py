import json

from django.test import TestCase
from django.urls import reverse
from django.core import mail

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article

from rest_framework.test import APIClient


class BaseTestClass(TestCase):


    def setUp(self):

        self.user_data = {

                "username": "sampleuser",
                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
        }

        self.user_data2 = {

                "username": "sampleuser2",
                "email": "user@sprinters2.ug",
                "password": "Butt3rfly12"
        }

        self.login_data = {

                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
        }

        self.login_data_user2 = {

                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
        }

        self.article_data = {

                "title": "how to train your dragon",
                "description": "ever wonder how to do that?",
                "body": "you have to beleive"
            }

        self.update_data = {

                "title": "how to train your dragon again",
                "description": "ever wonder how to do that again?",
                "body": "you have to beleive again"

            }

        self.client = APIClient()


        self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(reverse('auth:login'), content_type='application/json',
                                data=json.dumps(self.user_data))

        self.test_token = login_resp.data.get("auth_token")
        self.auth_header = 'Bearer {}'.format(self.test_token)

        self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data2))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(reverse('auth:login'), content_type='application/json',
                                data=json.dumps(self.login_data_user2))

        self.test_token2 = login_resp.data.get("auth_token")
        self.auth_header2 = 'Bearer {}'.format(self.test_token2)
