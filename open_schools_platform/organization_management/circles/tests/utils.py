from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import create_circle
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.student_management.students.services import create_student


def create_test_circle() -> Circle:
    organization = create_organization(name="test_org", inn="1111111111")
    circle = create_circle(organization=organization, name="test_circle", address="d", capacity=0, description="alalal")
    return circle


def create_student_and_add_to_the_circle(i, circle):
    student = create_student(name=f"test_student{i}")
    student.circle = circle
    student.save()

    return student
