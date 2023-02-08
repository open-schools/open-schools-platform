import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
import pytz

from open_schools_platform.user_management.users.services import verify_token
from open_schools_platform.user_management.users.tests.utils import create_test_token, create_test_user


class UserExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.token_creation_url = reverse("api:user-management:users:create-token")
        self.token_verification_url = lambda pk: reverse(
            'api:user-management:users:verification-phone-by-token', args=[pk])
        self.user_creation_url = reverse("api:user-management:users:user")
        self.token_data_resend_url = lambda pk: reverse("api:user-management:users:get-token", args=[pk])
        self.sms_resend_url = lambda pk: reverse("api:user-management:users:resend", args=[pk])
        self.user_reset_password_url = reverse("api:user-management:users:reset-password")

    def test_firebase_response_is_not_200(self):
        token_creation_data = {
            "phone": "+79020000000",
            "recaptcha": "123456"
        }
        token_creation_response = self.client.post(self.token_creation_url, token_creation_data)
        self.assertEqual(400, token_creation_response.status_code)

        token = create_test_token()

        token_verification_data = {
            "otp": "123456"
        }
        token_verification_response = self.client.patch(self.token_verification_url(token.key),
                                                        token_verification_data)
        self.assertEqual(400, token_verification_response.status_code)

    def test_token_does_not_exist(self):
        user_creation_data = {
            "token": "99999999-9999-9999-9999-999999999999",
            "name": "test_user",
            "password": "123456",
        }
        user_creation_response = self.client.post(self.user_creation_url, user_creation_data)
        self.assertEqual(404, user_creation_response.status_code)

        token_verification_data = {
            "otp": "123456"
        }
        token = "99999999-9999-9999-9999-999999999999"
        token_verification_response = self.client.patch(self.token_verification_url(token),
                                                        token_verification_data)
        self.assertEqual(404, token_verification_response.status_code)

        sms_resend_data = {
            "recaptcha": "123456"
        }
        sms_resend_response = self.client.post(self.sms_resend_url(token), sms_resend_data)
        self.assertEqual(404, sms_resend_response.status_code)

        token_data_resend_response = self.client.get(self.token_data_resend_url(token))
        self.assertEqual(404, token_data_resend_response.status_code)

        password_reset_data = {
            "token": token,
            "password": "123456",
        }
        password_reset_response = self.client.post(self.user_reset_password_url,
                                                   password_reset_data)
        self.assertEqual(404, password_reset_response.status_code)

    def test_token_is_overdue(self):
        token = create_test_token()
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737, tzinfo=pytz.UTC)
        verify_token(token)

        user_creation_data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
        }
        user_creation_response = self.client.post(self.user_creation_url, user_creation_data)
        self.assertEqual(401, user_creation_response.status_code)

        token_verification_data = {
            "otp": "123456"
        }
        token_verification_response = self.client.patch(self.token_verification_url(token.key),
                                                        token_verification_data)
        self.assertEqual(401, token_verification_response.status_code)

        sms_resend_data = {
            "recaptcha": "123456"
        }
        sms_resend_response = self.client.post(self.sms_resend_url(token.key), sms_resend_data)
        self.assertEqual(401, sms_resend_response.status_code)

        password_reset_data = {
            "token": token.key,
            "password": "123456"
        }

        create_test_user()

        password_reset_response = self.client.post(self.user_reset_password_url, password_reset_data)
        self.assertEqual(401, password_reset_response.status_code)

    def test_token_is_not_verified(self):
        token = create_test_token()
        data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(401, response.status_code)

        password_reset_data = {
            "token": token.key,
            "password": "123456"
        }

        password_reset_response = self.client.post(self.user_reset_password_url,
                                                   password_reset_data)
        self.assertEqual(401, password_reset_response.status_code)

    def test_sms_cannot_be_resend(self):
        token = create_test_token()
        data = {
            "recaptcha": "123456"
        }
        response = self.client.post(self.sms_resend_url(token.key), data)
        self.assertEqual(400, response.status_code)

    def test_user_does_not_exist(self):
        token = create_test_token()
        verify_token(token)
        password_reset_data = {
            "token": token.key,
            "password": "123456"
        }

        password_reset_response = self.client.post(self.user_reset_password_url,
                                                   password_reset_data)

        self.assertEqual(404, password_reset_response.status_code)
