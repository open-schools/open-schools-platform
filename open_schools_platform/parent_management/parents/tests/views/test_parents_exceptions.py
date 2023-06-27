from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyStudentProfilesListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)
        self.invite_parent_queries_list_url = reverse("api:parent-management:parents:invite-parent-list")

    def test_queries_do_not_exist(self):
        response = self.client.get(self.invite_parent_queries_list_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data['results']))
