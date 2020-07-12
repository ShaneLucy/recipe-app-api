from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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
        # test fails as the user is created before the
        # api request to create the user
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password is greater than 5 characters"""
        payload = {
            'email': 'test@hotmail.com',
            'password': 'pass',
            'name': 'test'
        }
        # this section passes if the api responds with a bad request
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # this assertion verifies that the user details werent inserted into db
        user_exists = get_user_model().objects.filter(
            email=payload['email'],
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for a user"""
        payload = {
            'email': 'test@hotmail.com',
            'password': 'password123',
            'name': 'test'
        }
        # create user with payload and then issue a token to that user
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        # test passes if the response contains a token key and
        # api responds with ok
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that a token is not created if invalid credentials are given"""
        create_user(email='test@hotmail.com',
                    password='password123', name='test')
        payload = {
            'email': 'test@hotmail.com',
            'password': 'incorrectpasswordforthisuser',
        }
        response = self.client.post(TOKEN_URL, payload)
        # test fails if token isn't present in response
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that a token is not created if a user doesn't exist"""
        payload = {
            'email': 'test@hotmail.com',
            'password': 'incorrectpasswordforthisuser',
        }
        response = self.client.post(TOKEN_URL, payload)
        # test fails if token isn't present in response
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        """Test that email and password are required to create a token"""
        response = self.client.post(
            TOKEN_URL, {'email': 'one', 'password': ''})
        # test fails if token isn't present in response
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorised(self):
        """Test that authentication is required for users"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUsersApiTests(TestCase):
    """Test api requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test3@hotmail.com',
            password='password123',
            name='Test3'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """Test that post is not allowed on the me url"""
        response = self.client.post(ME_URL)

        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'email': 'testupdate@hotmail.com',
            'password': 'passwordupdate123',
            'name': 'test update'
        }
        response = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
