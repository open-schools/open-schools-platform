from django.contrib.gis.geos import Point
from geopy.geocoders import GoogleV3
from rest_framework.exceptions import NotAcceptable
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.common.constants import CommonConstants


def create_circle(name: str, organization: Organization, description: str, capacity: int, address: str,
                  location: Point = None) -> Circle:
    """
    Geopy library allows to take coordinates from address.

    If address is provided and location isn't, geopy will take coordinates from address. They will
    be put into location field (as Point object). If geopy won't be able to take coordinates from address,
    or limit of api requests to Nominatim will be exceeded, NotAcceptable exception will be raised.

    If you don't want geopy to take coordinates from address, then you can just pass location as
    argument in create_circle function (for example, if you want to create test circle). By default,
    location has None value.
    """
    if location is None:
        geolocator = GoogleV3(api_key=CommonConstants.GOOGLE_MAPS_API_KEY)
        try:
            coordinates = geolocator.geocode(address, timeout=CommonConstants.GEOPY_GEOCODE_TIMEOUT)
            if coordinates is None:
                raise NotAcceptable("Address is incorrect.")
            location = Point(coordinates.latitude, coordinates.longitude)
        except GeocoderUnavailable or GeocoderTimedOut:
            raise NotAcceptable("Geopy error appeared. Probably address is incorrect.")
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
