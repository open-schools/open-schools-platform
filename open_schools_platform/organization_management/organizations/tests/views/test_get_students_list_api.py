from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.circles.tests.utils import create_student_and_add_to_the_circle
from open_schools_platform.organization_management.employees.services import create_employee
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CirclesStudentsListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)

        self.organization = create_organization(inn="12345678901234567890", name="VeryFamousOrg")
        create_employee(name="Van", user=self.user, organization=self.organization, position="Master of fantasy")
        self.circle = create_circle(address="Dungeon str", capacity=34, description="private circle",
                                    name="Van's circle",
                                    organization=self.organization)
        self.reverse_url = reverse("api:organization-management:organizations:students-list")

        self.students = GetRequestTesting.create_testdata_in_db(
            creation_count=100,
            creation_function=create_student_and_add_to_the_circle,
            creation_function_args={"circle": self.circle}
        )

    def test_successful_response_for_simple_request(self):
        response = self.client.get(self.reverse_url, data={"circle__organization": self.organization.id})
        self.assertListEqual(self.students,
                             GetRequestTesting.get_results(response))

        response = self.client.get(self.reverse_url, data={"circle": self.circle.id})
        self.assertListEqual(self.students,
                             GetRequestTesting.get_results(response))

        response = self.client.get(self.reverse_url, data={"circle": self.circle.id,
                                                           "circle__organization": self.organization.id})
        self.assertListEqual(self.students,
                             GetRequestTesting.get_results(response))

    def test_require_at_least_one_field(self):
        response = self.client.get(self.reverse_url)
        self.assertEqual(406, response.status_code)
