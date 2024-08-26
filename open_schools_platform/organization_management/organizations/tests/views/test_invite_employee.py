import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.employees.selectors import get_employee_profile, get_employee
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class InviteEmployeeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.invite_employee_url = \
            lambda pk: reverse("api:organization-management:organizations:invite-employee", args=[pk])

    @pytest.mark.skip(reason="We should mock email and sms send method")
    def test_invite_employee_query_successfully_formed(self):
        create_logged_in_user(instance=self)
        organization = create_test_organization()
        data = {
            "email": "example_email@fds.ru",
            "phone": "+79020000000",
            "body": {
                "name": "test_user",
                "position": "test_position",
            }
        }
        response = self.client.post(self.invite_employee_url(str(organization.id)), data, format="json")
        self.assertEqual(201, response.status_code)
        employee_profile = get_employee_profile(filters={"name": data["body"]["name"]})
        self.assertTrue(employee_profile)
        self.assertTrue(get_employee(filters={"name": "test_user"}))
        self.assertEqual(1, Query.objects.count())
