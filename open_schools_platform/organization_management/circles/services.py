import datetime
import typing
from typing import Dict, Callable, Tuple, Type

import pytz
from django.contrib.gis.geos import Point
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from geopy.geocoders import GoogleV3
from icalendar import Calendar, Event
from rest_framework.exceptions import ValidationError
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import re

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.errors.exceptions import QueryCorrupted
from open_schools_platform.organization_management.circles.constants import weekday_abbreviation
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.selectors import get_organization
from open_schools_platform.organization_management.teachers.models import TeacherProfile
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.models import Student
from open_schools_platform.common.constants import CommonConstants
from open_schools_platform.student_management.students.selectors import get_student_profile
from open_schools_platform.tasks.tasks import send_circle_lesson_notification
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
                raise ValidationError({'address': 'Address is incorrect'})
            location = Point(coordinates.longitude, coordinates.latitude)
        except GeocoderUnavailable or GeocoderTimedOut:
            raise ValidationError("Geopy error appeared. Probably address is incorrect.")
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
    available_statuses: Dict[Tuple[str, str], Tuple] = {
        (Query.Status.SENT, 'teachers.teacher_profile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, 'families.family_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, 'circles.circle_access'): (Query.Status.CANCELED,),
    }

    @typing.no_type_check
    def query_to_family(self, query: Query):
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise QueryCorrupted()
            query.body.circle = query.sender
            query.body.student_profile = query.additional
            query.body.save()

    @typing.no_type_check
    def query_to_teacher_profile(self, query: Query):
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise QueryCorrupted()
            query.body.circle = query.sender
            query.body.teacher_profile = query.recipient
            query.body.save()

    change_query: Dict[Type, Callable[[typing.Any, Query], Query]] = {
        Family: query_to_family,
        TeacherProfile: query_to_teacher_profile
    }


setattr(Circle, "query_handler", CircleQueryHandler())


def add_student_to_circle(student: Student, circle: Circle):
    student.circle = circle
    student.save()


def is_organization_related_to_student_profile(organization_id: str, student_profile: str, user: User = None):
    return len(get_organization(filters={"id": organization_id}, user=user, empty_exception=True).students.filter(
        id__in=map(lambda student: student.id, get_student_profile(
            filters={"id": student_profile}, empty_exception=True).students.all())
    )) > 0


def convert_str_to_point(string: str):
    res = re.findall(r"\d+\.\d+", string)
    return Point(float(res[0]), float(res[1]), srid=4326)


def setup_scheduled_notification(circle: Circle, minutes_before: int):
    name = f'{minutes_before}minutes_{circle.id}'
    task = PeriodicTask.objects.filter(name=name)
    if len(task) == 0:
        cron = create_crontab_schedule(circle, datetime.timedelta(minutes=minutes_before))
        create_periodic_task(circle, cron, name)
    elif task[0].description != str(circle.start_time):
        task = task[0]
        CrontabSchedule.objects.filter(id=task.crontab.id).delete()
        cron = create_crontab_schedule(circle, datetime.timedelta(minutes=minutes_before))
        task.crontab = cron
        task.save()


def setup_scheduled_notifications(circle: Circle):
    setup_scheduled_notification(circle, 60)
    setup_scheduled_notification(circle, 24 * 60)


def create_crontab_schedule(circle: Circle, timedelta: datetime.timedelta) -> CrontabSchedule:
    time = circle.start_time.astimezone(pytz.UTC) - timedelta  # type: ignore[union-attr]
    cron = CrontabSchedule.objects.create(
        timezone='UTC',
        minute=time.minute,
        hour=time.hour,
        day_of_week=time.isoweekday() % 7,
        day_of_month='*',
        month_of_year='*',
    )
    return cron


def create_periodic_task(circle: Circle, cron: CrontabSchedule, name) -> PeriodicTask:
    periodic_task = PeriodicTask.objects.create(
        name=name,
        task=send_circle_lesson_notification.name,
        crontab=cron,
        args=f'["{circle.id}"]',
        description=circle.start_time,
        enabled=True
    )
    return periodic_task


def generate_ical(queryset):
    cal = Calendar()
    cal.add('prodid', '-//LamArt//Open Schools//')
    cal.add('version', '2.0')
    if not isinstance(queryset, typing.Iterable):
        queryset = [queryset]
    for circle in queryset:
        if not circle.start_time:
            continue
        event = Event()
        event.add('summary', circle.name)
        event.add('dtstart', circle.start_time)
        event.add('dtend', circle.start_time + (circle.duration or datetime.timedelta(hours=1)))
        event.add('dtstamp', circle.created_at)
        event.add('rrule', {'freq': 'weekly', 'byday': weekday_abbreviation[circle.start_time.weekday()]})
        event.add('geo', (circle.latitude, circle.longitude))
        cal.add_component(event)
    return cal.to_ical()
