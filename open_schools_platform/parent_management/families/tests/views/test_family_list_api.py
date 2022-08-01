from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.parent_management.families.tests.utils import create_test_family

from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyListApi(TestCase):
    def setUp(self):
        self.family_count = 100
        self.client = APIClient()

        user = create_logged_in_user(instance=self)
        self.reverse_url = reverse("api:parent-management:families:family-api")

        self.families = GetRequestTesting.create_testdata_in_db(
            creation_count=self.family_count,
            creation_function=create_test_family,
            creation_function_args={"parent": user.parent_profile}
        )

    def test_families_list_api(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(200, response.status_code)

    def test_response(self):
        response = self.client.get(self.reverse_url)
        self.assertListEqual(self.families,
                             GetRequestTesting.get_results(response))
