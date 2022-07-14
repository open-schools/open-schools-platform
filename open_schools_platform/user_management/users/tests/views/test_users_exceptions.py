import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
import pytz

from open_schools_platform.user_management.users.services import verify_token
from open_schools_platform.user_management.users.tests.utils.test_utils import create_test_token, \
    create_not_logged_in_user


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
        data_for_token_creation_request = {
            "phone": "+79020000000",
            "recaptcha": "123456"
        }
        response_for_token_creation_request = self.client.post(self.token_creation_url, data_for_token_creation_request)
        self.assertEqual(422, response_for_token_creation_request.status_code)

        token = create_test_token()

        data_for_token_verification_request = {
            "otp": "123456"
        }
        response_for_token_verification_request = self.client.put(self.token_verification_url(token.key),
                                                                  data_for_token_verification_request)
        self.assertEqual(422, response_for_token_verification_request.status_code)

    def test_token_does_not_exist(self):
        data_for_user_creation_request = {
            "token": "99999999-9999-9999-9999-999999999999",
            "name": "test_user",
            "password": "123456",
        }
        response_for_user_creation_request = self.client.post(self.user_creation_url, data_for_user_creation_request)
        self.assertEqual(404, response_for_user_creation_request.status_code)

        data_for_token_verification_request = {
            "otp": "123456"
        }
        token = "99999999-9999-9999-9999-999999999999"
        response_for_token_verification_request = self.client.put(self.token_verification_url(token),
                                                                  data_for_token_verification_request)
        self.assertEqual(404, response_for_token_verification_request.status_code)

        data_for_sms_resend_request = {
            "recaptcha": "123456"
        }
        response_for_sms_resend_request = self.client.post(self.sms_resend_url(token), data_for_sms_resend_request)
        self.assertEqual(404, response_for_sms_resend_request.status_code)

        response_for_token_data_resend_request = self.client.get(self.token_data_resend_url(token))
        self.assertEqual(404, response_for_token_data_resend_request.status_code)

        data_for_password_reset_request = {
            "token": token,
            "password": "123456",
        }
        response_for_password_reset_request = self.client.post(self.user_reset_password_url,
                                                               data_for_password_reset_request)
        self.assertEqual(404, response_for_password_reset_request.status_code)

    def test_token_is_overdue(self):
        token = create_test_token()
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737, tzinfo=pytz.UTC)
        verify_token(token)

        data_for_user_creation_request = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
        }
        response_for_user_creation_request = self.client.post(self.user_creation_url, data_for_user_creation_request)
        self.assertEqual(401, response_for_user_creation_request.status_code)

        data_for_token_verification_request = {
            "otp": "123456"
        }
        response_for_token_verification_request = self.client.put(self.token_verification_url(token.key),
                                                                  data_for_token_verification_request)
        self.assertEqual(401, response_for_token_verification_request.status_code)

        data_for_sms_resend_request = {
            "recaptcha": "123456"
        }
        response_for_sms_resend_request = self.client.post(self.sms_resend_url(token.key), data_for_sms_resend_request)
        self.assertEqual(401, response_for_sms_resend_request.status_code)

        data_for_password_reset = {
            "token": token.key,
            "password": "123456"
        }

        create_not_logged_in_user()

        response_for_password_reset = self.client.post(self.user_reset_password_url, data_for_password_reset)
        self.assertEqual(401, response_for_password_reset.status_code)

    def test_token_is_not_verified(self):
        token = create_test_token()
        data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(401, response.status_code)

        data_for_password_reset_request = {
            "token": token.key,
            "password": "123456"
        }

        create_not_logged_in_user()
        response_for_password_reset_request = self.client.post(self.user_reset_password_url,
                                                               data_for_password_reset_request)
        self.assertEqual(401, response_for_password_reset_request.status_code)

    def test_sms_cannot_be_resend(self):
        token = create_test_token()
        data = {
            "recaptcha": "123456"
        }
        response = self.client.post(self.sms_resend_url(token.key), data)
        self.assertEqual(422, response.status_code)

    def test_user_does_not_exist(self):
        token = create_test_token()
        verify_token(token)

        data_for_password_reset_request = {
            "token": token.key,
            "password": "123456"
        }

        response_for_password_reset_request = self.client.post(self.user_reset_password_url,
                                                               data_for_password_reset_request)

        self.assertEqual(404, response_for_password_reset_request.status_code)
