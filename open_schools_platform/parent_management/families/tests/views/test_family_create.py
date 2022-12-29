from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.family_create_url = reverse("api:parent-management:families:family-api")

    def test_successful_family_creation(self):
        create_logged_in_user(instance=self)
        family_creation_data = {
            "name": "test_name"
        }
        family_creation_response = self.client.post(self.family_create_url, family_creation_data)
        self.assertEqual(201, family_creation_response.status_code)
        self.assertEqual(1, Family.objects.count())

    def test_name_generates_automatically_if_its_not_provided(self):
        user = create_logged_in_user(instance=self)
        self.client.post(self.family_create_url)
        family = get_family(filters={"parent_profiles": str(user.parent_profile.id)})
        self.assertTrue(family.name)
