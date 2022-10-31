import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user, create_test_user


class EmployeeExceptions(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.edit_employee_url = lambda pk: \
            reverse("api:organization-management:employees:edit-employee", args=[pk])

    def test_update_employee_does_not_exist(self):
        create_logged_in_user(instance=self)
        data = {
            "name": "new_name"
        }
        response = self.client.put(self.edit_employee_url(pk="99999999-9999-9999-9999-999999999999"), data)
        self.assertEqual(404, response.status_code)

    def test_delete_employee_does_not_exist(self):
        create_logged_in_user(instance=self)
        response = self.client.delete(self.edit_employee_url(pk=uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_delete_employee_wrong_access(self):
        create_logged_in_user(self)
        employee = create_test_employee(user=create_test_user("+79993218888"), organization=create_test_organization())
        response = self.client.delete(self.edit_employee_url(pk=str(employee.id)))
        self.assertEqual(403, response.status_code)
