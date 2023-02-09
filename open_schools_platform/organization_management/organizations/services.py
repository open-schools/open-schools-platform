from django.db.models import QuerySet
import typing

from open_schools_platform.common.filters import BaseFilterSet
from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.common.utils import form_ids_string_from_queryset, get_dict_including_fields, \
    convert_str_date_to_datetime
from open_schools_platform.errors.exceptions import QueryCorrupted
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.student_management.students.selectors import get_students


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


def organization_circle_query_filter(view, filters, organization: Organization, circle: Circle):
    queries = Query.objects.all()
    if organization:
        if organization.circles.values():
            queries &= get_queries(
                filters={"recipient_ids": form_ids_string_from_queryset(organization.circles.values())}
            )
        else:
            return Query.objects.none()
    if circle:
        queries &= get_queries(filters={"recipient_id": circle.id})

    queries &= get_queries(
        filters=BaseFilterSet.get_dict_filters_without_prefix(
            get_dict_including_fields(filters, view.FilterProperties.query_fields.keys())
        )
    )

    students = get_students(
        filters=BaseFilterSet.get_dict_filters_without_prefix(
            get_dict_including_fields(filters, view.FilterProperties.student_fields.keys())
        )
    )

    if students:
        queries &= get_queries(filters={"body_ids": form_ids_string_from_queryset(students)})
    else:
        return Query.objects.none()

    return queries


def filter_organization_circle_queries_by_dates(queries: QuerySet, date_from, date_to):
    return queries.filter(created_at__range=[convert_str_date_to_datetime(date_from, "00:00:00"),
                                             convert_str_date_to_datetime(date_to, "23:59:59")])
