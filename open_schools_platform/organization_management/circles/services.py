from typing import Dict, Callable, Tuple, Type

from django.contrib.gis.geos import Point
from geopy.geocoders import GoogleV3
from rest_framework.exceptions import NotAcceptable, ValidationError, MethodNotAllowed
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import re

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.parent_management.families.models import Family
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


def query_to_family(query: Query, new_status: str):
    query_update(query=query, data={"status": new_status})
    if query.status == Query.Status.ACCEPTED:
        if query.body is None:
            raise MethodNotAllowed("put", detail="Query is corrupted")
        query.body.circle = query.sender
        query.body.student_profile = query.additional
        query.body.save()
    return query


def query_to_teacher_profile(query: Query, new_status: str):
    query_update(query=query, data={"status": new_status})
    if query.status == Query.Status.ACCEPTED:
        if query.body is None:
            raise MethodNotAllowed("put", detail="Query is corrupted")
        query.body.circle = query.sender
        query.body.teacher_profile = query.recipient
        query.body.save()
    return query


def query_wrong_recipient(query: Query, new_status: str):
    raise ValidationError(detail="The recipient must be a Family or TeacherProfile if the sender is a circle")


class CircleQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED, Query.Status.DECLINED]
    available_statuses: Dict[Tuple[str, frozenset], Tuple] = {
        (Query.Status.SENT, frozenset({'teachers.teacher_profile_access', 'circles.circle_access'})): (
            Query.Status.DECLINED, Query.Status.CANCELED, Query.Status.ACCEPTED),
        (Query.Status.SENT, frozenset({'teachers.teacher_profile_access'})): (
            Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, frozenset({'circles.circle_access'})): (Query.Status.CANCELED,),

        (Query.Status.SENT, frozenset({'families.family_access'})): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, frozenset({'families.family_access', 'circles.circle_access'})): (
            Query.Status.DECLINED, Query.Status.CANCELED, Query.Status.ACCEPTED),
    }
    change_query: Dict[Type, Callable[[Query, str], Query]] = {
        Family: query_to_family,
        TeacherProfile: query_to_teacher_profile
    }

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(CircleQueryHandler, query, new_status, user)

        change_query_function = CircleQueryHandler.change_query.get(type(query.recipient), query_wrong_recipient)
        access_type = CircleQueryHandler._parse_changer_type(user, query)

        if new_status in CircleQueryHandler.available_statuses[(query.status, access_type)]:
            return change_query_function(query, new_status)
        else:
            raise NotAcceptable(
                f'Status change [{query.status} => {new_status}] not allowed' +
                f'{", no access permissions" if len(access_type) == 0 else f"for permission {access_type}"}')

    setattr(Circle, "query_handler", query_handler)

    @staticmethod
    def _parse_changer_type(user: User, query: Query) -> frozenset:
        result = set()
        required_permissions = set([item for key in CircleQueryHandler.available_statuses.keys() for item in key[1]])
        for required_permission in required_permissions:
            try:
                if user.has_perm(required_permission, query.sender):
                    result.add(required_permission)
            except AttributeError:
                pass
            try:
                if user.has_perm(required_permission, query.recipient):
                    result.add(required_permission)
            except AttributeError:
                pass

        return frozenset(result)


def add_student_to_circle(student: Student, circle: Circle):
    student.circle = circle
    student.save()


def convert_str_to_point(string: str):
    res = re.findall(r"\d+\.\d+", string)
    return Point(float(res[0]), float(res[1]), srid=4326)
