from django.test import TestCase

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.tests.utils.test_utils import create_test_circle


class CreateCircleTests(TestCase):
    def test_successful_circle_creation(self):
        create_test_circle()
        self.assertEqual(1, Circle.objects.count())
