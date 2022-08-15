from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CirclesStudentsListApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.get_circle_url = lambda pk: reverse("api:organization-management:circles:get-circle", args=[pk])

    def test_successfully_get_circle(self):
        create_logged_in_user(instance=self)
        circle = create_test_circle()
        response = self.client.get(self.get_circle_url(pk=str(circle.id)))
        self.assertEqual(200, response.status_code)
