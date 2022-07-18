from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization


def create_circle(name: str, organization: Organization) -> Circle:
    circle = Circle.objects.create(
        name=name,
        organization=organization,
    )
    return circle
