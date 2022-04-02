import requests
from django.test import TestCase


from open_schools_platform.users.constants import RegistrationConstants


class GoogleApiKeyTests(TestCase):
    def setUp(self):
        pass

    def test_google_api_key(self):
        base_url = RegistrationConstants.FIREBASE_URL_TO_GET_SESSION + \
                   RegistrationConstants.GOOGLE_API_KEY

        response = requests.post(base_url)
        self.assertEqual(400, response.status_code)
