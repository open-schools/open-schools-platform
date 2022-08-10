from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class EmployeeExceptions(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.update_employee_url = lambda pk: \
            reverse("api:organization-management:employees:update_employee", args=[pk])

    def test_employee_does_not_exist(self):
        create_logged_in_user(instance=self)
        data = {
            "name": "new_name"
        }
        response = self.client.put(self.update_employee_url(pk="99999999-9999-9999-9999-999999999999"), data)
        self.assertEqual(404, response.status_code)
