import json

from django.urls import reverse
from rest_framework import status

from authors.apps.authentication.tests.test_base import BaseTestClass


class TestUserProfile(BaseTestClass):

    def test_retrieve_profile_without_logging_in_fails(self):
        response = self.client.get(f'/api/profiles/{self.test_user.username}',
                                   content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_profile_with_valid_token_succeeds(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(self.verified_user_login_credentials))

        response = self.client.get(
            '/api/profiles/sampleuser',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.verified_user_login_token())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('sampleuser', response.data['username'])

    def test_edit_my_profile_succeeds(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(self.verified_user_login_credentials))

        response = self.client.put(
            '/api/profiles/sampleuser/edit',
            content_type='application/json',
            data=json.dumps(self.profile_data),
            HTTP_AUTHORIZATION=self.verified_user_login_token()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_authenticated_user_view_author_profiles_fails(self):
        response = self.client.get(reverse('profiles:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_view_author_profiles_succeeds(self):
        response = self.client.get(
            reverse('profiles:profile-list'),
            HTTP_AUTHORIZATION=self.verified_user_login_token())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_following_unauthorised(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.verified_user_login_credentials))
        response = self.client.post(
            '/api/profiles/sampleuser/follow',
            content_type='application/json')
        message = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, message)

    def test_following_success(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.verified_user_login_credentials))
        response = self.client.post(
            '/api/profiles/sampleuser/follow',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.verified_user_login_token())
        self.assertEqual(response.status_code, 200)

    def test_unfollowing_unauthorised(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.verified_user_login_credentials))
        response = self.client.delete(
            '/api/profiles/sampleuser/follow',
            content_type='application/json')
        message = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, message)

    def test_unfollowing_success(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.verified_user_login_credentials))
        response = self.client.post(
            '/api/profiles/sampleuser/follow',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.verified_user_login_token())
        response = self.client.delete(
            '/api/profiles/sampleuser/follow',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.verified_user_login_token())
        self.assertEqual(response.status_code, 200)

    def test_user_followers_unauthorised(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.verified_user_login_credentials))
        response = self.client.get(
            '/api/profiles/sampleuser/followers',
            content_type='application/json')
        message = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, message)

    def test_user_followers_success(self):
        sign_up_response = self.client.post(
            reverse('auth:login'),
            content_type='application/json',
            data=json.dumps(
                self.verified_user_login_credentials))
        response = self.client.get(
            '/api/profiles/sampleuser/followers',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.verified_user_login_token())
        self.assertEqual(response.status_code, 200)
