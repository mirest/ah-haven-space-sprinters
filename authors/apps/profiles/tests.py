import json
from authors.apps.authentication.tests.test_base import BaseTestClass
from rest_framework import status

from django.urls import reverse
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
