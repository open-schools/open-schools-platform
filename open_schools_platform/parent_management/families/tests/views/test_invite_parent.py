from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.parent_management.families.tests.utils import create_test_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class FamilyInviteParentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.invite_parent_url = reverse("api:parent-management:families:invite-parent")

    def test_invite_parent_query_successfully_formed(self):
        user = create_logged_in_user(instance=self)
        family = create_test_family(parent=user.parent_profile, i=1)
        parent = create_test_user(phone="+79022222222")
        data = {
            "family": str(family.id),
            "phone": str(parent.phone),
        }
        response = self.client.post(self.invite_parent_url, data, format="json")
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, Query.objects.count())
