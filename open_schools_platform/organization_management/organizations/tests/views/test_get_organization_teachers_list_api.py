from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.organization_management.teachers.tests.utils import create_teacher_and_add_to_circle
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class OrganizationTeachersListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)
        self.organization = create_test_organization()
        create_test_employee(user=self.user, organization=self.organization)
        self.circle = create_test_circle(organization=self.organization)
        self.teachers = GetRequestTesting.create_testdata_in_db(
            creation_count=100,
            creation_function=create_teacher_and_add_to_circle,
            creation_function_args={"circle": self.circle}
        )
        self.get_teachers_url = lambda pk: reverse("api:organization-management:organizations:teachers-list", args=[pk])

    def test_successful_response(self):
        response = self.client.get(self.get_teachers_url(pk=str(self.organization.pk)))
        self.assertListEqual(self.teachers, GetRequestTesting.get_results(response))
