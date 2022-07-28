from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization


def create_circle(name: str, organization: Organization, description: str, capacity: int, address: str) -> Circle:
    circle = Circle.objects.create(
        name=name,
        organization=organization,
        description=description,
        address=address,
        capacity=capacity
    )
    return circle
