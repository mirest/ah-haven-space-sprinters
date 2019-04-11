from django.test import TestCase

from authors.apps.authentication.models import User


class TestUserModel(TestCase):
    def test_create_super_user(self):
        user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@sprinters.ug')
        self.assertEqual(user.is_staff, True)

    def test_create_user_with_no_email(self):
        with self.assertRaises(TypeError):
            user = User.objects.create_user(
                username="rhytah", email=None, password='mypassword')

    def test_create_user_with_no_username(self):
        with self.assertRaises(TypeError):
            user = User.objects.create_user(
                username=None,
                email='sprinter1@space.com',
                password='mypassword')

    def test_return_str__method(self):
        self.user = User.objects.create_user(
            username="nandi",
            email="sprinter2@space.com",
            password='nandipassword')
        self.assertEqual(self.user.__str__(), 'sprinter2@space.com')

    def test_return_short_name__method(self):
        self.user = User.objects.create_user(
            username="leila",
            email="sprinter3@space.com",
            password='leilapassword')
        self.assertEqual('leila', self.user.get_short_name())

    def test_return_full_name__method(self):
        self.user = User.objects.create_user(
            username="rhytah",
            email="sprinter1@space.com",
            password='mypassword')
        self.assertEqual('rhytah', self.user.get_full_name)
