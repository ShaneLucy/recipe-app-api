from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTests(TestCase):
    """Test the users API public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with a valid payload is successful"""
        payload = {
            'email': 'test@hotmail.com',
            'password': 'password123',
            'name': 'test'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        # check that the api responds with created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # verify that the user was inserted into db
        user = get_user_model().objects.get(**response.data)
        self.assertEqual(user.email, payload['email'])
        # verify that the password isn't returned in the response
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test creating a user already exists fails"""
        payload = {
            'email': 'test@hotmail.com',
            'password': 'password123',
            'name': 'test'
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is greater than 5 characters"""
        payload = {
            'email': 'test@hotmail.com',
            'password': 'pass',
            'name': 'test'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email'],
        ).exists()
        self.assertFalse(user_exists)
