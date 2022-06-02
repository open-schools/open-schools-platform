from django.test import TestCase
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.services import verify_token
from open_schools_platform.user_management.users.tests.views.test_services import valid_token_for_tests_creation


class UserRequestsCycleTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.token_creation_url = "/api/user-management/users/token"
        self.token_verification_url = "/api/user-management/users/token/{}/verify"
        self.user_creation_url = "/api/user-management/users/"

    def test_user_token_creation(self):
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
        data_for_token_creation = {
            "phone": "+79025456481",
            "recaptcha": "123456"
        }
        token = valid_token_for_tests_creation(data=data_for_token_creation)
        response = self.client.put(self.token_verification_url.format(token.key), data)
        self.assertEqual(200, response.status_code)

    def test_user_creation(self):
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
