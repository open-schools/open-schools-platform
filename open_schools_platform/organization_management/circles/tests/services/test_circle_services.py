from django.test import TestCase

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.services import create_organization


class CreateCircleTests(TestCase):
    def test_successful_circle_creation(self):
        organization = create_organization(name="test_org", inn="1111111111")
        create_circle(name="test_circle", organization=organization)
        self.assertEqual(1, Circle.objects.count())
