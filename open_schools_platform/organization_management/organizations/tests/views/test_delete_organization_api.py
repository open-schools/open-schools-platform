from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle, get_deleted_circles
from open_schools_platform.organization_management.organizations.selectors import get_organizations
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization, \
    get_deleted_organizations, create_test_employees
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class OrganizationDeleteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.delete_organization_url = lambda pk: \
            reverse("api:organization-management:organizations:delete-organization", args=[pk])

    def test_successfully_delete_organization(self):
        user = create_logged_in_user(self)
        organization = create_test_organization()
        create_test_employees(user, [organization, ])
        response = self.client.delete(self.delete_organization_url(pk=str(organization.pk)))
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(get_organizations()))
        self.assertEqual(1, len(get_deleted_organizations()))

    def test_successfully_delete_circles(self):
        user = create_logged_in_user(self)
        organization = create_test_organization()
        create_test_employees(user, [organization, ])
        create_test_circle(organization=organization, name="circle1")
        create_test_circle(organization=organization, name="circle2")
        create_test_circle(organization=organization, name="circle3")
        response = self.client.delete(self.delete_organization_url(pk=str(organization.pk)))
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(get_organizations()))
        self.assertEqual(0, len(get_circles()))
        self.assertEqual(1, len(get_deleted_organizations()))
        self.assertEqual(3, len(get_deleted_circles()))
