from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.user_management.users.models import User


def create_test_circle() -> Circle:
    organization = create_organization(name="test_org", inn="1111111111")
    circle = create_circle(organization=organization, name="test_circle", address="d", capacity=0, description="alalal")
    return circle


def create_test_circle_with_user_in_org(user: User) -> Circle:
    organization = create_organization(name="test_org", inn="1111111111")
    employee = create_test_employee(user=user)
    organization.employees.add(employee)
    circle = create_circle(organization=organization, name="test_circle", address="d", capacity=0, description="alalal")
    return circle
