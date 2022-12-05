from django.contrib.gis.geos import Point
from geopy.geocoders import GoogleV3
from rest_framework.exceptions import NotAcceptable, ValidationError, MethodNotAllowed
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import re

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.common.constants import CommonConstants
from open_schools_platform.user_management.users.models import User


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
            location = Point(coordinates.longitude, coordinates.latitude)
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


class CircleQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED, Query.Status.DECLINED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(CircleQueryHandler, query, new_status, user)

        from open_schools_platform.parent_management.families.models import Family
        circle_access = user.has_perm('circles.circle_access', query.sender)

        if type(query.recipient) is Family:
            family_access = user.has_perm('families.family_access', query.recipient)

            if not family_access:
                if new_status != Query.Status.CANCELED:
                    raise NotAcceptable("Circle can only set canceled status")
            elif not circle_access:
                if query.status != Query.Status.SENT:
                    raise NotAcceptable("Сan no longer change the query")
                if new_status == Query.Status.CANCELED:
                    raise NotAcceptable("User cannot cancel query, he can only decline or accept it")

            query_update(query=query, data={"status": new_status})
            if query.status == Query.Status.ACCEPTED:
                if query.body is None:
                    raise MethodNotAllowed("put", detail="Query is corrupted")
                query.body.circle = query.sender
                query.body.student_profile = query.additional
                query.body.save()
            return query

        if type(query.recipient) is TeacherProfile:
            teacher_profile_access = user.has_perm("teachers.teacher_profile_access", query.recipient)

            if teacher_profile_access and circle_access:
                pass
            elif circle_access:
                if query.status != Query.Status.SENT:
                    raise NotAcceptable("Сan no longer change the query")
                if new_status != Query.Status.CANCELED:
                    raise NotAcceptable("Circle can only set canceled status")
            elif teacher_profile_access:
                if query.status == Query.Status.CANCELED:
                    raise NotAcceptable("Сan no longer change the query")
                if new_status == Query.Status.CANCELED:
                    raise NotAcceptable("Teacher cannot cancel query, it can only decline it")

            query_update(query=query, data={"status": new_status})
            if query.status == Query.Status.ACCEPTED:
                if query.body is None:
                    raise MethodNotAllowed("put", detail="Query is corrupted")
                query.body.circle = query.recipient
                query.body.teacher_profile = query.sender
                query.body.save()
            return query
        raise ValidationError(detail="The recipient must be a Family or TeacherProfile if the sender is a circle")

    setattr(Circle, "query_handler", query_handler)


def add_student_to_circle(student: Student, circle: Circle):
    student.circle = circle
    student.save()


def convert_str_to_point(string: str):
    res = re.findall(r"\d+\.\d+", string)
    return Point(float(res[0]), float(res[1]), srid=4326)
