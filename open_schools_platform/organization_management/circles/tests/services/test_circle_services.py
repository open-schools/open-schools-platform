import pytest
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle


class CreateCircleTests(TestCase):
    def test_successful_circle_creation(self):
        create_test_circle()
        self.assertEqual(1, Circle.objects.count())


class GetCoordinatesFromAddressTests(TestCase):
    @pytest.mark.skip
    def test_successfully_got_coordinates_from_address(self):
        circle = create_test_circle(address='175 5th Avenue NYC', location=None)
        self.assertTrue(circle.location != Point(0.0, 0.0))

    @pytest.mark.skip
    def test_incorrect_address(self):
        self.assertRaises(
            ValidationError, lambda: create_test_circle(address="12345678910", location=None))
