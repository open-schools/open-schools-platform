from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.employees.selectors import get_employees
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee, \
    get_deleted_employees
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CircleDeleteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.edit_employee_url = lambda pk: reverse("api:organization-management:employees:employee", args=[pk])

    def test_successfully_delete_employee(self):
        user = create_logged_in_user(self)
        employee = create_test_employee(user=user, organization=create_test_organization())
        response = self.client.delete(self.edit_employee_url(pk=str(employee.id)))
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(get_employees()))
        self.assertEqual(1, len(get_deleted_employees()))
