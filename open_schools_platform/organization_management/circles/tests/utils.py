from typing import Any

from django.contrib.gis.geos import Point

from open_schools_platform.common.filters import SoftCondition
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.circles.services import create_circle, add_student_to_circle
from open_schools_platform.organization_management.employees.tests.utils import create_test_employee
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.tests.utils import create_test_organization
from open_schools_platform.user_management.users.models import User
from open_schools_platform.student_management.students.services import create_student


def create_test_circle(organization: Organization = None, address: str = "address",
                       location: Any = Point(0.0, 0.0), name: str = "test_circle",
                       capacity: int = 10, description: str = "description") -> Circle:
    if not organization:
        organization = create_test_organization()
    circle = create_circle(
        organization=organization,  # type: ignore
        name=name,
        address=address,
        capacity=capacity,
        description=description,
        location=location
    )
    return circle


def create_test_circle_with_user_in_org(user: User) -> Circle:
    employee = create_test_employee(user)
    employee.organization = create_test_organization()
    employee.save()
    circle = create_test_circle(employee.organization)
    return circle


def create_student_and_add_to_the_circle(i, circle):
    student = create_student(name=f"test_student{i}")
    add_student_to_circle(student=student, circle=circle)

    return student


def get_deleted_circles():
    circles = get_circles(filters={'DELETED': SoftCondition.DELETED_ONLY})
    return circles
