from typing import List

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.common.tests.test_utils import GetRequestTesting
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organizations, \
    create_test_employees
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class InviteEmployeeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_logged_in_user(instance=self)
        self.get_organizations_url = reverse("api:organization-management:organizations:organization-api")
        self.organizations = create_test_organizations()

    def get_organizations_test(self, organizations: List[Organization]):
        create_test_employees(user=self.user, organizations=organizations)
        response = self.client.get(self.get_organizations_url)
        self.assertCountEqual([str(item.id) for item in organizations],
                              GetRequestTesting.get_results(response))

    def test_get_organizations_1(self):
        organizations = [self.organizations[1]]
        self.get_organizations_test(organizations)

    def test_get_organizations_2(self):
        organizations = [self.organizations[0], self.organizations[3]]
        self.get_organizations_test(organizations)

    def test_get_organizations_3(self):
        organizations = []
        self.get_organizations_test(organizations)
