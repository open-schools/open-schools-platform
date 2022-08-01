from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.parent_management.families.services import create_family
from open_schools_platform.parent_management.families.tests.utils import create_student_profile_in_family
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class FamilyStudentProfilesListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)
        self.family = create_family(parent=self.user.parent_profile, name="test_family")

        self.student_profiles = GetRequestTesting \
            .create_testdata_in_db(
                creation_count=100,
                creation_function=create_student_profile_in_family,
                creation_function_args={"family": self.family}
            )

        self.reverse_url = reverse("api:parent-management:families:student-profiles-list", args=[self.family.id])

    def test_studentprofiles_list_api(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(200, response.status_code)

    def test_response(self):
        response = self.client.get(self.reverse_url)
        self.assertListEqual(self.student_profiles,
                             GetRequestTesting.get_results(response), "wrong data in response")
