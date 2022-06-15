from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from open_schools_platform.user_management.users.services import verify_token
from open_schools_platform.user_management.users.tests.views.test_utils import valid_token_for_tests_creation


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
        # make sure this number is listed in firebase
        data = {
            "otp": "123456"
        }
        data_for_token_creation = {
            "phone": "+79025456481",
            "recaptcha": "123456"
        }
        token = valid_token_for_tests_creation(data=data_for_token_creation)
        response = self.client.put(self.token_verification_url(token.key), data)
        self.assertEqual(200, response.status_code)

    def test_user_creation(self):
        # make sure this number is listed in firebase
        data_for_token_creation = {
            "phone": "+79025456481",
            "recaptcha": "123456"
        }

        token = valid_token_for_tests_creation(data=data_for_token_creation)
        verify_token(token)
        data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
            "password_confirm": "123456"
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(201, response.status_code)
