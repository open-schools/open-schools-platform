from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle_with_user_in_org
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.student_management.students.tests.utils import create_test_student
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class OrganizationStudentsExportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.export_students_url = lambda pk: reverse(
            "api:organization-management:organizations:export-organization-students", args=[pk])

    def test_successfully_export_students(self):
        user = create_logged_in_user(self)
        organization = create_test_organization()
        circle = create_test_circle_with_user_in_org(user, organization)
        create_test_student(circle=circle)
        response = self.client.get(self.export_students_url(organization.pk))
        self.assertEqual(200, response.status_code)
