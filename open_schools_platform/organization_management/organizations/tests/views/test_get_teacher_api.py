from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.organization_management.teachers.tests.utils import create_test_teacher
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class GetTeacherTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_teacher_url = \
            lambda pk: reverse("api:organization-management:organizations:get-teacher", args=[pk])

    def test_successfully_get_teacher_as_his_owner(self):
        user = create_logged_in_user(self)
        circle = create_test_circle()
        teacher = create_test_teacher(circle=circle, teacher_profile=user.teacher_profile)
        response = self.client.get(self.get_teacher_url(pk=str(teacher.pk)))
        self.assertEqual(200, response.status_code)

    def test_successfully_get_teacher_as_employee_in_his_circles_organization(self):
        user = create_logged_in_user(self)
        organization = create_test_organization()
        create_test_employee(user=user, organization=organization)
        circle = create_test_circle(organization=organization)
        teacher = create_test_teacher(circle=circle, teacher_profile=create_test_user("+79020000000").teacher_profile)
        response = self.client.get(self.get_teacher_url(pk=str(teacher.pk)))
        self.assertEqual(200, response.status_code)
