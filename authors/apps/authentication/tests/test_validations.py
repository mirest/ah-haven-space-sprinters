import json

from django.urls import reverse

from .test_base import BaseTestClass


class TestRegistrationValidation(BaseTestClass):
    """This class tests the functionality of the registration validation
    Examples:
    - Registration with a very short password
    - Registration with non alphanumeric password
    - Registration with an already existing email
    """

    def test_register_with_short_password_fails(self):
        expected_response = {
            "errors": {
                "password": ["Password must be longer than 8 characters."]}}
        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json',
                                data=json.dumps({"username": "jake",
                                                 "email": "jake@gmail.com",
                                                 "password": "jake"}))
        self.assertDictEqual(resp.data, expected_response)
        self.assertIn(
            "Password must be longer than 8 characters.", str(
                resp.data))

    def test_register_with_invalid_password_fails(self):
        expected_response = {"errors": {"password": [
            "Password should at least contain a number, capital and small letter."]}}
        resp = self.client.post(reverse('auth:register'),
                                content_type='application/json',
                                data=json.dumps({"username": "naira",
                                                 "email": "naira@gmail.com",
                                                 "password": "dancinggal"}))
        self.assertDictEqual(resp.data, expected_response)
        self.assertIn(
            "Password should at least contain a number, capital and small letter.", str(
                resp.data))

    def test_register_with_existing_email_fails(self):
        expected_response = {"errors": {"email": ["Email already exists."]}}
        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data))
        resp = self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.same_email_user))
        self.assertDictEqual(resp.data, expected_response)
        self.assertIn("Email already exists.", str(resp.data))

    def test_register_with_existing_username_fails(self):
        expected_response = {
            "errors": {
                "username": ["Username already exists."]}}
        self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.user_data))
        resp = self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.same_username_user))
        self.assertDictEqual(resp.data, expected_response)
        self.assertIn("Username already exists.", str(resp.data))

    def test_register_with_invalid_username_fails(self):
        expected_response = {"errors": {"username": [
            "username cannot be integers, have white spaces or symbols."]}}
        resp = self.client.post(
            reverse('auth:register'),
            content_type='application/json',
            data=json.dumps(
                self.invalid_username))
        self.assertDictEqual(resp.data, expected_response)
        self.assertIn(
            "username cannot be integers, have white spaces or symbols.", str(
                resp.data))
