from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
import json
from authors.apps.authentication.models import User
from .test_base import BaseTestClass


class TestUserRoutes(BaseTestClass):
    def test_user_regsitration_with_valid_data_succeeds(self):

        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('sampleuser', str(resp.data))

    def test_login_user_with_valid_data(self):
        user = User.objects.create_user(username='testuser',
                                             password='testpassword', email='tester@sprinters.ug')
        verified_user_login_credentials = {
            "user": {
                "email": "tester@sprinters.ug",
                "password": "testpassword"
            }}
        resp = self.client.post(reverse('auth:login'), content_type='application/json',
                                data=json.dumps(verified_user_login_credentials))
        self.assertEqual(resp.status_code, 200)

    def test_login_with_invalid_user_fails(self):
        expected_response = {
            "errors": {
                "error": [
                    "A user with this email and password was not found."
                ]
            }
        }
        resp = self.client.post(reverse('auth:login'),
                                content_type='application/json', data=json.dumps(self.invalid_user))
        self.assertDictEqual(resp.data, expected_response)
        self.assertIn(
            "A user with this email and password was not found.", str(resp.data))

    # test whether a token is generated on login
    
    def test_login_user_login_token(self):
        user=User.objects.create_user(username='sampleuser', email='user@sprinters.ug',password='Butt3rfly1')
        user.is_active=True
        user.save()
        user_login_credentials = {
            "user": {
                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
            }}

        response = self.client.post(
            reverse('auth:login'),
            data=user_login_credentials,
            format='json')
        self.assertIn('auth_token', response.data)
        self.assertEqual(response.status_code, 200)

# test whether a token is generated on signup
    def test_signup_user_signup_token(self):
        response = self.client.post(
            reverse('auth:register'),
            data=self.user_data,
            format='json')
        self.assertIn('auth_token', response.data)
        self.assertEqual(response.status_code, 201)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer dffg.ssddd.ghg5')
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertIn(
            "Invalid authentication. Could not decode token.", str(response.data))
        self.assertEqual(response.status_code, 403)


    def test_user_with_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header_token())
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_upate_user_no_auth_token_header(self):
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertIn(
            "Authentication credentials were not provided.", str(response.data))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth_header_prefix(self):
        self.client.credentials(HTTP_AUTHORIZATION='token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImhocGtsbXVyampra2trZyIsImV4cCI6MTU1NTAxMTg0M30.7eLjTWCAisjs8mwrfsmlrqPNcO13bv3Tp_t8Xi-okms')
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertIn(
            "Authentication credentials were not provided.", str(response.data))
        self.assertEqual(response.status_code, 403)

    def test_invalid_length_of_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='bearer ssds.fdfd gfggg')
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertEqual(response.status_code, 403)



