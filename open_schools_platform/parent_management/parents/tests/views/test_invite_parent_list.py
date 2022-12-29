from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.parent_management.families.tests.utils import create_test_family
from open_schools_platform.query_management.queries.tests.utils import create_test_family_invite_parent_query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class FamilyStudentProfilesListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)
        self.family = create_test_family(i=1, parent=create_test_user(phone="+79021111111").parent_profile)
        self.queries = GetRequestTesting.create_testdata_in_db(
            creation_count=4,
            creation_function=create_test_family_invite_parent_query,
            creation_function_args={
                "family": self.family,
                "user": self.user
            },
        )

        self.reverse_url = reverse("api:parent-management:parents:invite-parent-list")

    def test_successfully_get_invite_parent_queries(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(200, response.status_code)
        self.assertListEqual(self.queries, GetRequestTesting.get_results(response))
