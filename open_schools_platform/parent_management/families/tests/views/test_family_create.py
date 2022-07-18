from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family_create_url = reverse("api:parent-management:families:create-family")

    def test_successful_family_creation(self):
        user = create_logged_in_user(instance=self)
        data_for_family_creation = {
            "parent_profile": user.parent_profile.id,
            "name": "test_name"
        }

        response_for_family_creation = self.client.post(self.family_create_url, data_for_family_creation)
        self.assertEqual(201, response_for_family_creation.status_code)

    def test_name_generates_automatically_if_its_not_provided(self):
        user = create_logged_in_user(instance=self)
        data_for_family_creation = {
            "parent_profile": user.parent_profile.id,
        }

        self.client.post(self.family_create_url, data_for_family_creation)
        family = get_family(filters={"parents": user.parent_profile.id})
        self.assertTrue(family.name)
