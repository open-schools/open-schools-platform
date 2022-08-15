from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.student_management.students.models import Student


def create_circle(name: str, organization: Organization, description: str, capacity: int, address: str,
                  latitude: float, longitude: float) -> Circle:
    circle = Circle.objects.create(
        name=name,
        organization=organization,
        description=description,
        address=address,
        capacity=capacity,
        latitude=latitude,
        longitude=longitude
    )
    return circle


def add_student_to_circle(student: Student, circle: Circle):
    student.circle = circle
    student.save()
