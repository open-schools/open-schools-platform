import calendar
from datetime import timedelta, datetime
import typing
from typing import Dict, Callable, Tuple, Type
import pandas as pd

import pytz
from django.contrib.gis.geos import Point
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from geopy.geocoders import GoogleV3
from icalendar import Calendar, Event
from rest_framework.exceptions import ValidationError
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import re

from open_schools_platform.common.services import BaseQueryHandler, model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.errors.exceptions import QueryCorrupted, MapServiceUnavailable
from open_schools_platform.organization_management.circles.constants import CirclesConstants
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


def create_circle(name: str, organization: Organization, address: str, description: str = None, capacity: int = 0,
                  start_time: datetime = None, duration: timedelta = None, location: Point = None) -> Circle:
    """
    Geopy library allows to take coordinates from address.

    If address is provided and location isn't, geopy will take coordinates from address. They will
    be put into location field (as Point object). If geopy won't be able to take coordinates from address,
    or limit of api requests to Nominatim will be exceeded, ValidationError exception will be raised.

    If you don't want geopy to take coordinates from address, then you can just pass location as
    argument in create_circle function (for example, if you want to create test circle). By default,
    location has None value.
    """
    if not location:
        api_key = CommonConstants.GOOGLE_MAPS_API_KEY
        if not api_key:
            raise MapServiceUnavailable(
                'Server cannot handle address. Please specify the \'location\' field explicitly')
        geolocator = GoogleV3(api_key=api_key)
        try:
            coordinates = geolocator.geocode(get_address_after_split_by_separator(address),
                                             timeout=CommonConstants.GEOPY_GEOCODE_TIMEOUT)
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
        location=location,
        start_time=start_time,
        duration=duration
    )

    return circle


class CircleQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED, Query.Status.DECLINED]
    available_statuses: Dict[Tuple[str, str], Tuple] = {
        (Query.Status.SENT, 'teachers.teacherprofile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
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


def get_address_after_split_by_separator(address: str):
    return address.split(CirclesConstants.ADDRESS_SEPARATOR)[0]


def setup_scheduled_notifications(circle: Circle, notification_delays: list[timedelta]):
    tasks = PeriodicTask.objects.filter(args=f'["{circle.id}"]', task=send_circle_lesson_notification.name)
    CrontabSchedule.objects.filter(id__in=list(map(lambda task: task.crontab.id, tasks))).delete()

    if circle.start_time is None:
        tasks.delete()
        return

    cron_list = list(map(lambda delta: create_crontab_schedule(circle, delta), notification_delays))
    if len(tasks) == 0 or len(tasks) != len(notification_delays):
        PeriodicTask.objects.filter(id__in=list(map(lambda task: task.id, tasks))).delete()
        create_periodic_tasks(circle, cron_list)
    else:
        for i in range(len(cron_list)):
            tasks[i].crontab = cron_list[i]
            tasks[i].name = CirclesConstants.task_name(cron_list[i], circle)
            tasks[i].save()


def create_crontab_schedule(circle: Circle, time_delta: timedelta):
    if circle.start_time is None:
        return None
    time = circle.start_time.astimezone(pytz.UTC) - time_delta
    cron = CrontabSchedule.objects.create(
        timezone='UTC',
        minute=time.minute,
        hour=time.hour,
        day_of_week=time.isoweekday() % 7,
        day_of_month='*',
        month_of_year='*',
    )
    return cron


def create_periodic_tasks(circle: Circle, cron_list: list[CrontabSchedule]) -> list[PeriodicTask]:
    periodic_tasks = []
    for cron in cron_list:
        periodic_task = PeriodicTask.objects.create(
            name=CirclesConstants.task_name(cron, circle),
            task=send_circle_lesson_notification.name,
            crontab=cron,
            args=f'["{circle.id}"]',
            enabled=True
        )
        periodic_tasks.append(periodic_task)
    return periodic_tasks


def update_circle(*, circle: Circle, data) -> Circle:
    non_side_effect_fields = ['name', 'address', 'location']
    filtered_data = filter_dict_from_none_values(data)
    circle, has_updated = model_update(
        instance=circle,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return circle


def generate_ical(queryset):
    cal = Calendar()
    cal.add('prodid', '-//Open Schools//')
    cal.add('version', '2.0')
    if not isinstance(queryset, typing.Iterable):
        queryset = [queryset]
    for circle in queryset:
        if not circle.start_time:
            continue
        event = Event()
        event.add('summary', circle.name)
        event.add('dtstart', circle.start_time)
        event.add('dtend', circle.start_time + (circle.duration or timedelta(hours=1)))
        event.add('dtstamp', circle.created_at)
        event.add('rrule', {'freq': 'weekly', 'byday': calendar.day_abbr[circle.start_time.weekday()][:2].upper()})
        event.add('geo', (circle.latitude, circle.longitude))
        cal.add_component(event)
    return cal.to_ical()


def create_invites_by_xlsx(file):
    ds = pd.read_excel(file)
    invites = []
    for row in ds.iterrows():
        name, student_phone, parent_phone, email = row[1].values
        invite = {
            'body': {
                'name': name
            },
            "student_phone": format_phones(str(student_phone)),
            "parent_phone": format_phones(str(parent_phone)),
            "email": email,
        }
        invites.append(invite)
    return invites


def format_phones(phone):
    if "+7" not in phone and '8' == phone[0]:
        phone = '+7' + phone[1:]
    elif "+" not in phone and '7' == phone[0]:
        phone = "+" + phone
    return phone

