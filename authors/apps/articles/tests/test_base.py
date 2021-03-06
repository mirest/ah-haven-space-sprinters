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
            "password": "Butt3rfly1"}
        self.user_data2 = {
            "username": "sampleuser2",
            "email": "user@sprinters2.ug",
            "password": "Butt3rfly12"}
        self.user_data3 = {
            "username": "sampleuser3",
            "email": "user3@sprinters.ug",
            "password": "Butt3rfly123"}
        self.login_data = {
            "email": "user@sprinters.ug",
            "password": "Butt3rfly1"}
        self.login_data_user2 = {
            "email": "user@sprinters.ug",
            "password": "Butt3rfly1"}
        self.login_data3 = {
            "email": "user3@sprinters.ug",
            "password": "Butt3rfly123"}
        self.article_data = {
            "title": "how to train your dragon",
            "description": "ever wonder how to do that?",
            "body": "you have to beleive"}
        self.article_data2 = {
            "title": "how to train your dragon",
            "description": "ever wonder how to do that?",
            "body": "you have to beleive",
            "tags": ["comedy", "education"]}
        self.update_data = {
            "title": "how to train your dragon again",
            "description": "ever wonder how to do that again?",
            "body": "you have to beleive again"}
        self.client = APIClient()
        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.user_data))
        self.test_token = login_resp.data.get("auth_token")
        self.auth_header = 'Bearer {}'.format(self.test_token)

        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data2))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.login_data_user2))
        self.test_token2 = login_resp.data.get("auth_token")
        self.auth_header2 = 'Bearer {}'.format(self.test_token2)

        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data3))
        verification_link = (mail.outbox[2].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.user_data3))
        self.test_token = login_resp.data.get("auth_token")
        self.auth_header3 = 'Bearer {}'.format(self.test_token)

        self.article_data = {
            "title": "how to train your dragon",
            "description": "ever wonder how to do that?",
            "body": "you have to beleive"
        }
        self.article = {
            "title": "how to train your dragon",
            "description": "ever wonder how to do that?",
            "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\
                         Nulla neque lorem, congue id purus nec, elementum aliquet leo.\
                         Aenean arcu est, auctor ac lacus vitae, posuere tincidunt dui.\
                        Aenean nisl diam, posuere sit amet libero vel, scelerisque iaculis ligula.\
                        Donec aliquam vitae erat et dictum. Integer erat odio, placerat ut egestas in,\
                        hendrerit in urna. Nulla luctus justo eu neque scelerisque, vitae consequat dui volutpat.\
                         Aenean sit amet condimentum nunc. Sed sollicitudin auctor nisl, ac molestie purus feugiat pharetra.\
                        In ut eros at est semper consequat nec at ligula. Etiam urna nisl, eleifend nec lobortis eget, cursus in ex.\
                        Nulla eu urna rhoncus, vehicula est auctor,\
                        semper magna. Nulla facilisi. Suspendisse potenti.\
                         Duis at risus leo. Suspendisse potenti. Vivamus fermentum,\
                         magna sit amet pharetra efficitur, nunc felis iaculis felis,\
                                 id vehicula nibh purus vitae ligula.\
                        sit amet sem et nulla posuere semper. Donec mi lorem,\
                         varius volutpat scelerisque eu, lacinia nec turpis.\
                         Aenean auctor ac odio id suscipit. Mauris eget dolor sed \
                        ligula efficitur mattis nec sed turpis. Donec volutpat gravida ligula,\
                         nec faucibus elit mollis sit amet. Integer varius eget est varius eleifend.\
                          Nullam laoreet est vitae congue fermentum. Nam vehicula, massa ac vehicula auctor,\
                         enim lectus porta erat, viverra tempus urna risus vitae purus.\
                        Nulla id mi felis. Proin mi nibh, pulvinar id enim eget, lacinia vestibulum dolor. \
                        In non quam in tellus convallis accumsan quis vitae massa.\
                        Maecenas et eros rutrum, consequat purus in, efficitur ipsum.\
                        Proin et neque id mauris porta condimentum ut in mi. Nam nisi lectus,\
                        efficitur vel sem at, dictum interdum metus. Praesent a dignissim lacus. \
                        Proin turpis lectus, pharetra sit amet turpis et, fringilla tincidunt turpis.\
                        Nam iaculis neque sit amet magna egestas, ut euismod ipsum lacinia. \
                        Pellentesque at magna vitae ipsum placerat dignissim. Nunc mi libero, commodo dictum ex ut,\
                        incidunt sodales erat. Praesent ac interdum nibh. Vivamus orci ligula, \
                        venenatis ut ligula id, pulvinar imperdiet diam.Morbi eleifend, \
                        lectus ut pulvinar lacinia, diam mauris cursus purus, \
                        quis ultricies orci felis nec purus. Vivamus vel eros eget arcu dignissim rhoncus. \
                                                                                                     Donec gravida non justo eu blandit. Vivamus massa nisi, suscipit. "
        }
        self.update_data = {
            "title": "how to train your dragon again",
            "description": "ever wonder how to do that again?",
            "body": "you have to beleive again"
        }
        self.email_share = {
            "email": "user@sprinters.ug",
        }
        self.url = reverse('article:create_article')
        self.like_url = '/api/articles/how-to-train-your-dragon/likes/'
        self.like_request = {
            "like_article": True
        }
        self.like_request_invalid = {
            "like_article": "True"
        }
        self.dislike_request = {
            "like_article": False
        }
        self.client = APIClient()
        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.user_data))

        self.test_token = login_resp.data.get("auth_token")
        self.auth_header = 'Bearer {}'.format(self.test_token)

        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data2))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        login_resp = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.login_data_user2))

        self.test_token2 = login_resp.data.get("auth_token")
        self.auth_header2 = 'Bearer {}'.format(self.test_token2)

        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data3))
        verification_link3 = (mail.outbox[2].body.split('\n')).pop(1)
        url3 = verification_link3.split("testserver").pop(1)
        self.client.get(url3, content_type='application/json')
        login_resp3 = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.user_data3))
        self.test_token3 = login_resp3.data.get("auth_token")
        self.auth_header3 = 'Bearer {}'.format(self.test_token3)
        self.slug = 'how-to-train-your-dragon'
        self.report_url = reverse('article:report', kwargs={'slug': self.slug})
