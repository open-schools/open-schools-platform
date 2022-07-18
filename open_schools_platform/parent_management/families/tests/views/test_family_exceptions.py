from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.tests.utils.test_utils import create_logged_in_user, \
    create_not_logged_in_user


class FamilyExceptionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family_create_url = reverse("api:parent-management:families:create-family")

    def test_parent_does_not_exist(self):
        create_logged_in_user(instance=self)
        data_for_family_creation = {
            "parent_profile": "99999999-9999-9999-9999-999999999999",
            "name": "test_name"
        }

        response_for_family_creation = self.client.post(self.family_create_url, data_for_family_creation)
        self.assertEqual(404, response_for_family_creation.status_code)

    def test_current_user_do_not_have_permission_to_create_family(self):
        user = create_not_logged_in_user()

        data_for_family_creation = {
            "parent_profile": user.parent_profile.id,
            "name": "test_name"
        }

        response_for_family_creation = self.client.post(self.family_create_url, data_for_family_creation)
        self.assertEqual(403, response_for_family_creation.status_code)
