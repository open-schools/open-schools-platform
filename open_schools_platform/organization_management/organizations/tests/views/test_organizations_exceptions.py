import uuid

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class OrganizationsExceptions(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.delete_organization_url = lambda pk: \
            reverse("api:organization-management:organizations:delete-organization", args=[pk])

    def test_delete_organization_does_not_exist(self):
        create_logged_in_user(instance=self)
        response = self.client.delete(self.delete_organization_url(pk=uuid.uuid4()))
        self.assertEqual(404, response.status_code)

    def test_delete_organization_wrong_access(self):
        create_logged_in_user(self)
        organization = create_test_organization()
        response = self.client.delete(self.delete_organization_url(pk=str(organization.pk)))
        self.assertEqual(403, response.status_code)
