from django.test import TestCase
from rest_framework.exceptions import NotAcceptable

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.circles.tests.utils import create_test_circle
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization


class CreateCircleTests(TestCase):
    def test_successful_circle_creation(self):
        create_test_circle()
        self.assertEqual(1, Circle.objects.count())


class GetCoordinatesFromAddressTests(TestCase):
    def test_successfully_got_coordinates_from_address(self):
        circle = create_circle(address='175 5th Avenue NYC', organization=create_test_organization(), capacity=10,
                               description='description', name='test_circle')
        self.assertTrue(circle.location)

    def test_incorrect_address(self):
        self.assertRaises(
            NotAcceptable, lambda: create_circle(
                address='12345678910',
                organization=create_test_organization(),
                capacity=10,
                description='description',
                name='test_circle')
            )


