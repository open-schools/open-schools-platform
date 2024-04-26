from django.db.models import QuerySet
import typing

from open_schools_platform.common.filters import SoftCondition
from open_schools_platform.common.services import BaseQueryHandler, ComplexFilter, ComplexMultipleFilter
from open_schools_platform.common.utils import convert_str_date_to_datetime
from open_schools_platform.errors.exceptions import QueryCorrupted
from open_schools_platform.organization_management.circles.filters import CircleFilter
from open_schools_platform.organization_management.circles.selectors import get_circles
from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.families.filters import FamilyFilter
from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.query_management.queries.filters import QueryFilter
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.student_management.students.filters import StudentProfileFilter, StudentFilter, \
    StudentProfileCircleAdditionalFilter
from open_schools_platform.student_management.students.selectors import get_students, get_student_profiles, \
    get_student_profiles_circle_additional
from django.contrib.contenttypes.models import ContentType

from open_schools_platform.ticket_management.tickets.filters import TicketFilter, TicketCommentFilter
from open_schools_platform.ticket_management.tickets.selectors import get_tickets, get_comments


def create_organization(name: str, inn: str = "") -> Organization:
    organization = Organization.objects.create(
        name=name,
        inn=inn,
    )
    return organization


class OrganizationQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED, Query.Status.DECLINED]
    available_statuses = {
        (Query.Status.SENT, 'employees.employeeprofile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
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


def get_organization_circle_query_filter():
    return ComplexMultipleFilter(
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
                include_list=["id", "phone", "parent_name", "parent_phone"],
            ),
            ComplexFilter(
                filterset_type=StudentFilter,
                selector=get_students,
                ids_field="body_ids",
                prefix="student",
                include_list=["id", "name", "student_profile__phone"],
                advance_filters_delegate=lambda: {"DELETED": SoftCondition.ALL}
            ),
            ComplexFilter(
                filterset_type=StudentProfileCircleAdditionalFilter,
                selector=get_student_profiles_circle_additional,
                ids_field='additional_ids',
                prefix="additional",
                include_list=["parent_phone", "parent_name", "text"]
            )
        ],
        filterset_type=QueryFilter,
        selector=get_queries,
        include_list=["status", "id", "created_at"],
        advance_filters_delegate=lambda: {
            "sender_ct": ContentType.objects.get(model="studentprofile"),
            "recipient_ct": ContentType.objects.get(model="circle"),
            "body_ct": ContentType.objects.get(model="student"),
            "additional_ct": ContentType.objects.get(model="studentprofilecircleadditional")
        },
        is_has_or_search_field=True,
    )


def get_organization_students_invitations_filter():
    return ComplexMultipleFilter(
        complex_filter_list=[
            ComplexFilter(
                filterset_type=CircleFilter,
                selector=get_circles,
                ids_field="sender_ids",
                prefix="circle",
                include_list=["id", "organization__id", "name", "address"],
            ),
            ComplexFilter(
                filterset_type=FamilyFilter,
                selector=get_families,
                ids_field="recipient_ids",
                prefix="family",
                include_list=["id", "name", "parent_phone"],
            ),
            ComplexFilter(
                filterset_type=StudentFilter,
                selector=get_students,
                ids_field="body_ids",
                prefix="student",
                include_list=["id", "name", "student_profile__phone"],
            ),
            ComplexFilter(
                filterset_type=StudentProfileFilter,
                selector=get_student_profiles,
                ids_field="additional_ids",
                prefix="student_profile",
                include_list=["id", "phone"],
            ),
        ],
        filterset_type=QueryFilter,
        selector=get_queries,
        include_list=["status", "id"],
        advance_filters_delegate=lambda: {
            "sender_ct": ContentType.objects.get(model="circle"),
            "recipient_ct": ContentType.objects.get(model="family"),
            "body_ct": ContentType.objects.get(model="student"),
            "additional_ct": ContentType.objects.get(model="studentprofile")
        },
        is_has_or_search_field=True,
    )


def filter_organization_circle_queries_by_dates(queries: QuerySet, date_from, date_to):
    return queries.filter(created_at__range=[convert_str_date_to_datetime(date_from, "00:00:00"),
                                             convert_str_date_to_datetime(date_to, "23:59:59")])


def get_family_organization_ticket_filter():
    return ComplexMultipleFilter(
        complex_filter_list=[
            ComplexFilter(
                filterset_type=FamilyFilter,
                selector=get_families,
                ids_field="sender_ids",
                prefix="family",
                include_list=["id", "name", "parent_phone"],
            ),
            ComplexFilter(
                filterset_type=TicketCommentFilter,
                selector=get_comments,
                ids_field="last_comment_ids",
                prefix="ticket_comment",
                include_list=["id", "value"],
            ),
        ],
        filterset_type=TicketFilter,
        selector=get_tickets,
        include_list=["status", "id", "created_at", "recipient_id", "recipient_ct"],
        advance_filters_delegate=lambda: {
            "sender_ct": ContentType.objects.get(model="family"),
            "recipient_ct": ContentType.objects.get(model="organization"),
        },
        is_has_or_search_field=True,
    )
