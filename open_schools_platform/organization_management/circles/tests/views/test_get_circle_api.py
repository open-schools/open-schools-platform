from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CirclesStudentsListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.circle_url = lambda pk: reverse("api:organization-management:circles:circle", args=[pk])

    def test_successfully_get_circle(self):
        user = create_logged_in_user(instance=self)
        organization = create_test_organization()
        circle = create_test_circle(organization)
        create_test_employee(user, organization)
        response = self.client.get(self.circle_url(pk=str(circle.id)))
        self.assertEqual(200, response.status_code)
