from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.parent_management.families.tests.utils import create_test_family, get_deleted_families
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyDeleteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.delete_family_url = lambda pk: reverse("api:parent-management:families:delete-family", args=[pk])

    def test_successfully_delete_family(self):
        user = create_logged_in_user(self)
        family = create_test_family(1, user.parent_profile)
        response = self.client.delete(self.delete_family_url(pk=str(family.pk)))
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(get_families()))
        self.assertEqual(1, len(get_deleted_families()))
