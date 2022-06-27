from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.services import verify_token, create_user
from open_schools_platform.user_management.users.tests.views.test_utils import valid_token_for_tests_creation


class UserResetPasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_reset_password_url = reverse("api:user-management:users:reset-password")

    def test_successful_password_reset(self):
        data_for_token_creation = {
            "phone": "+79025456481",
            "recaptcha": "123456"
        }

        token = valid_token_for_tests_creation(data=data_for_token_creation)
        verify_token(token)

        credentials = {
            "phone": "+79025456481",
            "password": "654321",
            "name": "test_user"
        }

        create_user(**credentials)

        data = {
            "token": token.key,
            "password": "123456"
        }
        response = self.client.post(self.user_reset_password_url, data)
        self.assertEqual(200, response.status_code)