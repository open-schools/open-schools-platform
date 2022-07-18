from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.services import create_organization


def create_test_circle() -> Circle:
    organization = create_organization(name="test_org", inn="1111111111")
    circle = create_circle(organization=organization, name="test_circle")
    return circle
