import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.user_management.users.tests.utils import create_logged_in_user


class CirclesIcalExportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        create_logged_in_user(self)
        self.export_single_circle = lambda pk: reverse("api:organization-management:circles:circle-ical", args=[pk])
        self.export_multiple_circles = reverse("api:organization-management:circles:circles-ical")

    def test_successfully_export_single_circle_schedule(self):
        circle = create_test_circle(start_time=datetime.datetime.fromtimestamp(1545730073))
        response = self.client.get(self.export_single_circle(circle.pk))
        self.assertEqual(200, response.status_code)

    def test_successfully_export_multiple_circles_schedule(self):
        create_test_circle(start_time=datetime.datetime.fromtimestamp(1545730073))
        create_test_circle(start_time=datetime.datetime.fromtimestamp(1545830073))
        create_test_circle(start_time=datetime.datetime.fromtimestamp(1555730073))
        response = self.client.get(self.export_multiple_circles)
        self.assertEqual(200, response.status_code)
