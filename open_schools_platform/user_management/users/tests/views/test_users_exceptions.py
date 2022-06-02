import datetime

from django.test import TestCase
from rest_framework.test import APIClient
import pytz

from open_schools_platform.user_management.users.services import create_user, create_token


class UserExceptionsTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.token_creation_url = "/api/user-management/users/token"
        self.token_verification_url = "/api/user-management/users/token/{}/verify"
        self.user_creation_url = "/api/user-management/users/"
        self.token_data_resend_url = "/api/user-management/users/token/{}"
        self.sms_resend_url = "/api/user-management/users/token/{}/resend"

    def test_user_already_created(self):
        credentials = {
            "phone": "+79020000000",
            "password": "123456",
            "name": "test_user"
        }

        create_user(**credentials)

        data_for_token_creation_request = {
            "phone": "+79020000000",
            "recaptcha": "123456"
        }

        response_for_token_creation_request = self.client.post(self.token_creation_url, data_for_token_creation_request)
        self.assertEqual(409, response_for_token_creation_request.status_code)

        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"  # invalid session, we use it only for testing
        }

        token = create_token(**data_for_token_creation)
        data_for_sms_resend_request = {
            "recaptcha": "123456"
        }
        response_for_sms_resend_request = self.client.post(self.sms_resend_url.format(token.key),
                                                           data_for_sms_resend_request)
        self.assertEqual(409, response_for_sms_resend_request.status_code)

    def test_firebase_response_is_not_200(self):
        data_for_token_creation_request = {
            "phone": "+79020000000",
            "recaptcha": "123456"
        }
        response_for_token_creation_request = self.client.post(self.token_creation_url, data_for_token_creation_request)
        self.assertEqual(400, response_for_token_creation_request.status_code)

        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"  # invalid session, we use it only for testing
        }
        token = create_token(**data_for_token_creation)

        data_for_token_verification_request = {
            "otp": "123456"
        }
        response_for_token_verification_request = self.client.put(self.token_verification_url.format(token.key),
                                                                  data_for_token_verification_request)
        self.assertEqual(400, response_for_token_verification_request.status_code)

    def test_token_does_not_exist(self):
        data_for_user_creation_request = {
            "token": "99999999-9999-9999-9999-999999999999",
            "name": "test_user",
            "password": "123456",
            "password_confirm": "123456"
        }
        response_for_user_creation_request = self.client.post(self.user_creation_url, data_for_user_creation_request)
        self.assertEqual(404, response_for_user_creation_request.status_code)

        data_for_token_verification_request = {
            "otp": "123456"
        }
        token = "99999999-9999-9999-9999-999999999999"
        response_for_token_verification_request = self.client.put(self.token_verification_url.format(token),
                                                                  data_for_token_verification_request)
        self.assertEqual(404, response_for_token_verification_request.status_code)

        data_for_sms_resend_request = {
            "recaptcha": "123456"
        }
        response_for_sms_resend_request = self.client.post(self.sms_resend_url.format(token), data_for_sms_resend_request)
        self.assertEqual(404, response_for_sms_resend_request.status_code)

        response_for_token_data_resend_request = self.client.get(self.token_data_resend_url.format(token))
        self.assertEqual(400, response_for_token_data_resend_request.status_code)

    def test_token_is_overdue(self):
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"  # invalid session, we use it only for testing
        }
        token = create_token(**data_for_token_creation)
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737, tzinfo=pytz.UTC)
        token.save()

        data_for_user_creation_request = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
            "password_confirm": "123456"
        }
        response_for_user_creation_request = self.client.post(self.user_creation_url, data_for_user_creation_request)
        self.assertEqual(408, response_for_user_creation_request.status_code)

        data_for_token_verification_request = {
            "otp": "123456"
        }
        response_for_token_verification_request = self.client.put(self.token_verification_url.format(token.key),
                                                                  data_for_token_verification_request)
        self.assertEqual(408, response_for_token_verification_request.status_code)

        data_for_sms_resend_request = {
            "recaptcha": "123456"
        }
        response_for_sms_resend_request = self.client.post(self.sms_resend_url.format(token.key), data_for_sms_resend_request)
        self.assertEqual(408, response_for_sms_resend_request.status_code)

    def test_token_is_not_verified(self):
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"        # invalid session, we use it only for testing
        }
        token = create_token(**data_for_token_creation)
        data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
            "password_confirm": "123456"
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(401, response.status_code)

    def test_sms_cannot_be_resend(self):
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"        # invalid session, we use it only for testing
        }

        token = create_token(**data_for_token_creation)
        data = {
            "recaptcha": "123456"
        }
        response = self.client.post(self.sms_resend_url.format(token.key), data)
        self.assertEqual(400, response.status_code)
