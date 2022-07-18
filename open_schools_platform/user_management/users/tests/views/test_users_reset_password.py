from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.selectors import get_user
from open_schools_platform.user_management.users.services import verify_token
from open_schools_platform.user_management.users.tests.utils import create_valid_test_token, create_not_logged_in_user


class UserResetPasswordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_reset_password_url = reverse("api:user-management:users:reset-password")

    def test_successful_password_reset(self):
        token = create_valid_test_token()
        verify_token(token)

        create_not_logged_in_user()

        data = {
            "token": token.key,
            "password": "123456"
        }
        response = self.client.post(self.user_reset_password_url, data)
        self.assertEqual(200, response.status_code)
        user = get_user(filters={"phone": "+79025456481"})
        self.assertTrue(user.check_password("123456"))
