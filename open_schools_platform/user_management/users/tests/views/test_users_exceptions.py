import datetime

from django.test import TestCase
from rest_framework.test import APIClient

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
            "password": "qwe",
            "name": "Vasya",
        }

        create_user(**credentials)

        data = {
            "phone": "+79020000000",
            "recaptcha": "123456"
        }
        response = self.client.post(self.token_creation_url, data)
        self.assertEqual(409, response.status_code)

    def test_firebase_response_is_not_200(self):
        data = {
            "phone": "+79020000000",
            "recaptcha": "123456"
        }
        response = self.client.post(self.token_creation_url, data)
        self.assertEqual(400, response.status_code)

    def test_token_with_such_id_does_not_exist(self):
        token = "99999999-9999-9999-9999-999999999999"
        response = self.client.get(self.token_data_resend_url.format(token))
        self.assertEqual(400, response.status_code)

    def test_token_does_not_exist_in_user_creation(self):
        data = {
            "token": "99999999-9999-9999-9999-999999999999",
            "name": "test_user",
            "password": "123456",
            "password_confirm": "123456"
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(404, response.status_code)

    def test_token_is_overdue(self):
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
        }
        token = create_token(**data_for_token_creation)
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737)
        token.save()
        data = {
            "token": token.key,
            "name": "test_user",
            "password": "123456",
            "password_confirm": "123456"
        }
        response = self.client.post(self.user_creation_url, data)
        self.assertEqual(408, response.status_code)

    def test_token_is_not_verified(self):
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
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

    def test_token_does_not_exist_in_token_verification(self):
        data = {
            "otp": "123456"
        }
        token = "99999999-9999-9999-9999-999999999999"
        response = self.client.put(self.token_verification_url.format(token), data)
        self.assertEqual(404, response.status_code)

    def test_token_is_overdue_in_token_verification(self):
        data = {
            "otp": "123456"
        }
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
        }
        token = create_token(**data_for_token_creation)
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737)
        token.save()
        response = self.client.put(self.token_verification_url.format(token.key), data)
        self.assertEqual(408, response.status_code)

    def test_firebase_response_in_token_verification_is_not_200(self):
        data = {
            "otp": "123456"
        }
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
        }
        token = create_token(**data_for_token_creation)
        response = self.client.put(self.token_verification_url.format(token.key), data)
        self.assertEqual(400, response.status_code)

    def test_token_does_not_exist_in_sms_resend(self):
        data = {
            "recaptcha": "123456"
        }
        token = "99999999-9999-9999-9999-999999999999"
        response = self.client.post(self.sms_resend_url.format(token), data)
        self.assertEqual(404, response.status_code)

    def test_token_is_overdue_in_sms_resend(self):
        data = {
            "recaptcha": "123456"
        }
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
        }

        token = create_token(**data_for_token_creation)
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737)
        token.save()
        response = self.client.post(self.sms_resend_url.format(token.key), data)
        self.assertEqual(408, response.status_code)

    def test_user_already_created_in_sms_resend(self):
        credentials = {
            "phone": "+79020000000",
            "password": "qwe",
            "name": "Vasya",
        }

        create_user(**credentials)

        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
        }

        token = create_token(**data_for_token_creation)
        data = {
            "recaptcha": "123456"
        }
        response = self.client.post(self.sms_resend_url.format(token.key), data)
        self.assertEqual(409, response.status_code)

    def test_sms_cannot_be_resend(self):
        data_for_token_creation = {
            "phone": "+79020000000",
            "session": "000000"
        }

        token = create_token(**data_for_token_creation)
        data = {
            "recaptcha": "123456"
        }
        response = self.client.post(self.sms_resend_url.format(token.key), data)
        self.assertEqual(400, response.status_code)
