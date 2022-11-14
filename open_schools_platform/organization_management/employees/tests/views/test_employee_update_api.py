from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.employees.selectors import get_employee
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class GettingEmployeesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.update_employee_url = lambda pk:\
            reverse("api:organization-management:employees:employee", args=[pk])

    def test_successfully_update_employee(self):
        user = create_logged_in_user(instance=self)
        employee = create_test_employee(user=user)
        data = {
            "name": "new_name"
        }
        response = self.client.put(self.update_employee_url(pk=str(employee.id)), data)
        self.assertEqual(200, response.status_code)
        self.assertEqual("new_name", get_employee(filters={"id": str(employee.id)}).name)
