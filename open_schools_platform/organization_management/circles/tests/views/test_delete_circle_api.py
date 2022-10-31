from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse

from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.circles.tests.utils import get_deleted_circles, \
    create_test_circle_with_user_in_org
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CircleDeleteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.circle_url = lambda pk: reverse("api:organization-management:circles:circle", args=[pk])

    def test_successfully_delete_circle(self):
        user = create_logged_in_user(self)
        circle = create_test_circle_with_user_in_org(user)
        response = self.client.delete(self.circle_url(pk=str(circle.id)))
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(get_circles()))
        self.assertEqual(1, len(get_deleted_circles()))
