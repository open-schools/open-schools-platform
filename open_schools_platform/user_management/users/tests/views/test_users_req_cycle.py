from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from open_schools_platform.user_management.users.services import verify_token
from open_schools_platform.user_management.users.tests.utils.test_utils import create_valid_test_token


class UserRequestsCycleTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.token_creation_url = reverse('api:user-management:users:create-token')
        self.user_creation_url = reverse('api:user-management:users:user')
        self.token_verification_url = lambda pk: reverse(
            'api:user-management:users:verification-phone-by-token', args=[pk])

    def test_user_token_creation(self):
        # make sure this number is listed in firebase
        data = {
            "phone": "+79025456481",
            "recaptcha": "123456"
        }
        response = self.client.post(self.token_creation_url, data)
        self.assertEqual(201, response.status_code)

    def test_user_token_verification(self):
        data = {
            "otp": "123456"
        }
        token = create_valid_test_token()
        response = self.client.put(self.token_verification_url(token.key), data)
        self.assertEqual(200, response.status_code)

    def test_user_creation(self):
        token = create_valid_test_token()
        verify_token(token)
        data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(201, response.status_code)
