from django.db.models import QuerySet
import typing

from open_schools_platform.common.services import BaseQueryHandler, ComplexFilter, ComplexMultipleFilter
from open_schools_platform.common.utils import convert_str_date_to_datetime
from open_schools_platform.errors.exceptions import QueryCorrupted
from open_schools_platform.organization_management.circles.filters import CircleFilter
from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.student_management.students.filters import StudentProfileFilter, StudentFilter
from open_schools_platform.student_management.students.selectors import get_students, get_student_profiles
from django.contrib.contenttypes.models import ContentType


def create_organization(name: str, inn: str = "") -> Organization:
    organization = Organization.objects.create(
        name=name,
        inn=inn,
    )
    return organization


class OrganizationQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED, Query.Status.DECLINED]
    available_statuses = {
        (Query.Status.SENT, 'employees.employee_profile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, 'organizations.organization_access'): (Query.Status.CANCELED,),
    }

    @typing.no_type_check
    def query_to_employee_profile(self, query: Query):
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise QueryCorrupted()
            query.body.organization = query.sender
            query.body.employee_profile = query.recipient
            query.body.save()

    change_query = {
        EmployeeProfile: query_to_employee_profile
    }


setattr(Organization, "query_handler", OrganizationQueryHandler())


organization_circle_query_filter = ComplexMultipleFilter(
    complex_filter_list=[
        ComplexFilter(
            filterset_type=CircleFilter,
            selector=get_circles,
            ids_field="recipient_ids",
            prefix="circle",
            include_list=["id", "organization__id", "name", "address"],
        ),
        ComplexFilter(
            filterset_type=StudentProfileFilter,
            selector=get_student_profiles,
            ids_field="sender_ids",
            prefix="student_profile",
            include_list=["id", "phone"],
        ),
        ComplexFilter(
            filterset_type=StudentFilter,
            selector=get_students,
            ids_field="body_ids",
            prefix="student",
            include_list=["id", "name", "student_profile__phone"],
        ),
    ],
    filterset_type=QueryFilter,
    selector=get_queries,
    include_list=["status", "id"],
    advance_filters={
        "sender_ct": ContentType.objects.get(model="studentprofile"),
        "recipient_ct": ContentType.objects.get(model="circle"),
        "body_ct": ContentType.objects.get(model="student"),
    },
    is_has_or_search_field=True,
)


def filter_organization_circle_queries_by_dates(queries: QuerySet, date_from, date_to):
    return queries.filter(created_at__range=[convert_str_date_to_datetime(date_from, "00:00:00"),
                                             convert_str_date_to_datetime(date_to, "23:59:59")])
