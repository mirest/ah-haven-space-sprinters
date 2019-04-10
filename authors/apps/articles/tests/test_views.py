import json

from django.urls import reverse

from rest_framework import status

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article

from .test_base import BaseTestClass


class TestUserRoutes(BaseTestClass):


    def test_create_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_all_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(
            reverse('article:create_article'), format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.get(
            reverse('article:get_article', kwargs={'slug':"how-to-train-your-dragon"}), format='json')
        self.assertEqual(response.status_code, 200)

    def test_slug_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.get(
            reverse('article:get_article', kwargs={'slug':"how-t-trai-your-dragon"}), format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found.', str(response.data))

    def test_delete_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.delete(
            reverse('article:get_article', kwargs={'slug':"how-to-train-your-dragon"}), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Article has been deleted', str(response.data))

    def test_update_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.put(
            reverse('article:get_article', kwargs={'slug':"how-to-train-your-dragon"}), data=self.update_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_article_no_slug(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.delete(
            reverse('article:get_article', kwargs={'slug':"how-to-train-your-dragon77"}), format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found.', str(response.data))

    def test_update_article_no_slug(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.put(
            reverse('article:get_article', kwargs={'slug':"how-to-train-your-dragon88"}), data=self.update_data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found.', str(response.data))

    def test_show_read_time(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article_data, format='json')
        response = self.client.get(
            reverse('article:get_article', kwargs={'slug': "how-to-train-your-dragon"}), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['read_time']), "less than 1 min")

    def test_show_read_time_more_than_a_minute(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'), data=self.article, format='json')
        response = self.client.get(
            reverse('article:get_article', kwargs={'slug': "how-to-train-your-dragon"}), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['read_time']), "4 mins")
