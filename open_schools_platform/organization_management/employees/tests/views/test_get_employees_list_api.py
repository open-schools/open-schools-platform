from typing import List, Dict

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.organization_management.employees.services import create_employee
from open_schools_platform.organization_management.employees.tests.utils import create_test_employees, \
    create_test_users, create_test_organizations
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class GettingEmployeesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)

        organizations = create_test_organizations()
        users = create_test_users()

        self.organization = organizations[0]
        self.employee = create_employee("Me", "Director", self.user, self.organization)
        self.get_employees_url = reverse("api:organization-management:employees:employees")
        self.employees = create_test_employees(users, organizations)

    def get_employees_test(self, correct_answers: List[str], data: Dict[str, str]):
        response = self.client.get(self.get_employees_url, data=data)
        self.assertCountEqual(correct_answers,
                              GetRequestTesting.get_results_for_argument(response=response, arg="phone"))

    def test_get_one_employee_by_name(self):
        correct_answers = ["+79999999902"]
        data = {
            "organization": self.organization.id,
            "name": "Alexander"
        }

        self.get_employees_test(correct_answers, data)

    def test_get_multiple_employee_by_name(self):
        correct_answers = ["+79999999901", "+79999999902"]
        data = {
            "organization": self.organization.id,
            "name": "A"
        }

        self.get_employees_test(correct_answers, data)

    def test_get_one_employee_by_phone(self):
        correct_answers = ["+79999999901"]
        data = {
            "organization": self.organization.id,
            "phone": "79999999901"
        }

        self.get_employees_test(correct_answers, data)

    def test_get_multiple_employees_by_part_of_phone(self):
        correct_answers = ["+79999999901", "+79999999902"]
        data = {
            "organization": self.organization.id,
            "phone": "+7999999990"
        }

        self.get_employees_test(correct_answers, data)

    def test_get_one_employee_by_search(self):
        correct_answers = ["+79999999902"]
        data = {
            "organization": self.organization.id,
            "search": "Chief cleaner"}

        self.get_employees_test(correct_answers, data)

    def test_get_multiple_employees_by_search(self):
        correct_answers = ["+79999999901", "+79999999902"]
        data = {
            "organization": self.organization.id,
            "search": "Chief"}

        self.get_employees_test(correct_answers, data)

    def test_get_employee_by_employee_profile(self):
        correct_answers = ["+79999999901"]
        data = {
            "organization": self.organization.id,
            "employee_profile": self.employees[0].employee_profile.id
        }

        self.get_employees_test(correct_answers, data)

    def test_get_one_employee_by_several_parameters(self):
        correct_answers = ["+79999999901"]
        data = {
            "organization": self.organization.id,
            "search": "Chief",
            "name": "A",
            "phone": "01",
        }

        self.get_employees_test(correct_answers, data)

    def test_get_multiple_employee_by_several_parameters(self):
        correct_answers = ["+79999999901", "+79999999902"]
        data = {
            "organization": self.organization.id,
            "search": "Chief",
            "name": "A",
        }

        self.get_employees_test(correct_answers, data)

    def test_get_no_one_employee(self):
        correct_answers = []
        data = {
            "organization": self.organization.id,
            "phone": "+79999999903"
        }

        self.get_employees_test(correct_answers, data)
