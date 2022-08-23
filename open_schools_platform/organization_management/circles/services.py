from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from rest_framework.exceptions import NotAcceptable

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.student_management.students.models import Student


def create_circle(name: str, organization: Organization, description: str, capacity: int, address: str) -> Circle:
    geolocator = Nominatim(user_agent="circles")
    coordinates = geolocator.geocode(address)
    if coordinates is None:
        raise NotAcceptable("Address is incorrect")
    location = Point(coordinates.latitude, coordinates.longitude)
    circle = Circle.objects.create_circle(
        name=name,
        organization=organization,
        description=description,
        address=address,
        capacity=capacity,
        location=location
    )

    return circle


def add_student_to_circle(student: Student, circle: Circle):
    student.circle = circle
    student.save()
