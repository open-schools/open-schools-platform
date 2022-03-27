from django.test import TestCase
import requests

from open_schools_platform.users.constants import RegistrationConstants


class FirebaseUrlsTests(TestCase):
    def setUp(self):
        pass

    def test_firebase_urls(self):
        response = requests.post(RegistrationConstants.FIREBASE_URL_TO_CHECK_OTP)
        self.assertEqual(403, response.status_code)

        response = requests.post(RegistrationConstants.FIREBASE_URL_TO_GET_SESSION)
        self.assertEqual(403, response.status_code)
