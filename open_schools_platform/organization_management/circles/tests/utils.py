from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.circles.services import create_circle, add_student_to_circle
from open_schools_platform.organization_management.employees.services import create_employee
from open_schools_platform.organization_management.organizations.services import create_organization
from open_schools_platform.user_management.users.models import User
from open_schools_platform.student_management.students.services import create_student


def create_test_circle() -> Circle:
    organization = create_organization(name="test_org", inn="1111111111")
    circle = create_circle(organization=organization, name="test_circle", address="d", capacity=0, description="alalal",
                           latitude=0.0, longitude=0.0)
    return circle


def create_test_circle_with_user_in_org(user: User) -> Circle:
    organization = create_organization(name="test_org", inn="1111111111")
    employee = create_employee(name="test_employee", position="test", user=user)
    employee.organization = organization
    employee.save()
    circle = create_circle(organization=organization, name="test_circle", address="d", capacity=0, description="alalal",
                           latitude=0.0, longitude=0.0)
    return circle


def create_student_and_add_to_the_circle(i, circle):
    student = create_student(name=f"test_student{i}")
    add_student_to_circle(student=student, circle=circle)

    return student
