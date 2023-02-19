import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.organization_management.teachers.tests.utils import create_test_teacher
from open_schools_platform.student_management.students.tests.utils import create_test_student
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class OrganizationsExceptions(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.delete_organization_url = lambda pk: \
            reverse("api:organization-management:organizations:delete-organization", args=[pk])
        self.export_students_url = lambda pk: reverse(
            "api:organization-management:organizations:export-organization-students", args=[pk])
        self.get_teachers_url = lambda pk: reverse("api:organization-management:organizations:teachers-list", args=[pk])
        self.get_teacher_url = lambda pk: reverse("api:organization-management:organizations:get-teacher", args=[pk])

    def test_delete_organization_does_not_exist(self):
        create_logged_in_user(instance=self)
        response = self.client.delete(self.delete_organization_url(pk=uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_delete_organization_wrong_access(self):
        create_logged_in_user(self)
        organization = create_test_organization()
        response = self.client.delete(self.delete_organization_url(pk=str(organization.pk)))
        self.assertEqual(403, response.status_code)

    def test_export_students_wrong_access(self):
        create_logged_in_user(self)
        organization = create_test_organization()
        circle = create_test_circle(organization)
        create_test_student(circle=circle)
        response = self.client.get(self.export_students_url(organization.pk))
        self.assertEqual(403, response.status_code)

    def test_teachers_list_organization_does_not_exist(self):
        create_logged_in_user(self)
        response = self.client.get(self.get_teachers_url(pk=uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_teachers_list_organization_has_no_circles(self):
        user = create_logged_in_user(self)
        organization = create_test_organization()
        create_test_employee(user=user, organization=organization)
        response = self.client.get(self.get_teachers_url(pk=str(organization.pk)))
        self.assertEqual(404, response.status_code)

    def test_get_teacher_does_not_exist(self):
        create_logged_in_user(self)
        response = self.client.get(self.get_teacher_url(pk=uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_get_teacher_wrong_access(self):
        create_logged_in_user(self)
        teacher = create_test_teacher(circle=create_test_circle(),
                                      teacher_profile=create_test_user("+79020000000").teacher_profile)
        response = self.client.get(self.get_teacher_url(pk=str(teacher.pk)))
        self.assertEqual(403, response.status_code)
