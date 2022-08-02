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

        organization = create_organization(inn="12345678901234567890", name="VeryFamousOrg")
        create_employee(name="Van", user=self.user, organization=organization, position="Master of fantasy")
        circle = create_circle(address="Dungeon str", capacity=34, description="private circle", name="Van's circle",
                               organization=organization)
        self.reverse_url = reverse("api:organization-management:circles:students-list", args=[circle.id])

        self.students = GetRequestTesting.create_testdata_in_db(
            creation_count=100,
            creation_function=create_student_and_add_to_the_circle,
            creation_function_args={"circle": circle}
        )

    def test_response(self):
        response = self.client.get(self.reverse_url)
        self.assertListEqual(self.students,
                             GetRequestTesting.get_results(response))
