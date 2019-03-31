import json

from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from authors.apps.authentication.models import User
from authors.apps.authentication.tokens import password_rest_token
from .test_base import BaseTestClass


class TestUserRoutes(BaseTestClass):
    def test_user_regsitration_with_valid_data_succeeds(self):
        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("Please check your email to verify your account verification has been sent to user@sprinters.ug",
                      str(resp.data))

    # verified user login with valid credentials
    def test_login_verified_user_with_valid_data(self):
        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(
            response.data['message'],
            "youve been verified")
        resp = self.client.post(reverse('auth:login'), content_type='application/json',
                                data=json.dumps(self.user_data))
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

    # test login unverified user

    def test_user_unverified(self):
        user = User.objects.create_user(username='sampleuser', email='user@sprinters.ug', password='Butt3rfly1')
        user.is_active = True
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
        expected_response = {
            "errors": {
                "error": [
                    "This user has not been verified, please check your email to verify."
                ]
            }
        }
        self.assertDictEqual(response.data, expected_response)
        self.assertIn(
            "This user has not been verified, please check your email to verify.", str(response.data))

    # test whether a token is generated on login

    def test_login_verified_user_login_token(self):
        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        response = self.client.get(url, content_type='application/json')

        response = self.client.post(
            reverse('auth:login'),
            data=self.user_data,
            format='json')
        self.assertIn('auth_token', response.data)
        self.assertEqual(response.status_code, 200)

    def test_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer dffg.ssddd.ghg5')
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertIn(
            "Invalid authentication. Could not decode token.", str(response.data))
        self.assertEqual(response.status_code, 403)

    def test_user_with_unverified_valid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header_token())
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertEqual(response.status_code, 403)

    def test_upate_user_no_auth_token_header(self):
        response = self.client.put(
            reverse('auth:updateRetrieve'),
            data=self.update_user,
            format='json')
        self.assertIn(
            "Authentication credentials were not provided.", str(response.data))
        self.assertEqual(response.status_code, 403)

    def test_wrong_auth_header_prefix(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImhocGtsbXVyampra2trZyIsImV4cCI6MTU1NTAxMTg0M30.7eLjTWCAisjs8mwrfsmlrqPNcO13bv3Tp_t8Xi-okms')
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

    # test invalid user details on login
    def test_invalid_login_data(self):
        resp = self.client.post(reverse('auth:login'), data=self.user_data, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('A user with this email and password was not found.', str(resp.data))

    # test invalid token
    def test_invalid_user_token(self):
        resp = self.client.get(reverse('auth:verify', kwargs={'token': 'fhfhgh'}))
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Invalid authentication. Could not decode token.", str(resp.data))

    # test already verified account
    def test_already_verified(self):
        self.client.post(reverse('auth:register'),
                         content_type='application/json', data=json.dumps(self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        self.client.get(url, content_type='application/json')
        response = self.client.get(url, content_type='application/json')
        self.assertIn('account has already been verified', str(response.data))
        self.assertEqual(response.status_code, 400)

    def test_rest_password_email(self):
        user = User.objects.create_user(username='sprintersspace',
                                        password='sprintersspacePassword',
                                        email='sprintersspace@gmail.com')
        user_reset_email = {"email": "sprintersspace@gmail.com"}
        message = {'message': 'Please check your email to confirm rest password',
                      'status_code': 200}
        response = self.client.post(reverse('auth:password_reset'),
                                    content_type='application/json', data=json.dumps(user_reset_email))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, message)

    def test_confirm_rest_password(self):
        user = User.objects.create_user(username='sprintersspace',
                                        password='sprintersspacePassword',
                                        email='sprintersspace@gmail.com')
        token = password_rest_token.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user)).decode()
        new_password = {'password1': 'Password123', 'password2': 'Password123'}
        response = self.client.post(f'/api/reset/{uidb64}/{token}',
                                    content_type='application/json', data=json.dumps(new_password))
        message = {'message': 'Password successfully updated',
                   'status_code': 200}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, message)
