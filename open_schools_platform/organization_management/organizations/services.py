from rest_framework.exceptions import ValidationError, PermissionDenied

from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.user_management.users.models import User


def create_organization(name: str, inn: str) -> Organization:
    organization = Organization.objects.create(
        name=name,
        inn=inn,
    )
    return organization


class OrganizationQueryHandler:
    # TODO: Add DECLINED status, may be add new AllowedStatus class
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        if new_status not in OrganizationQueryHandler.allowed_statuses:
            raise ValidationError(detail="Not allowed status")
        if user.employee_profile != query.recipient:
            raise PermissionDenied(detail="You have not access this query")
        if query.status == new_status:
            raise ValidationError(detail="Identical statuses")

        from open_schools_platform.organization_management.employees.models import EmployeeProfile

        if type(query.recipient) is not EmployeeProfile:
            raise ValidationError(detail="The recipient must be an Employee if the sender is an organization")

        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            query.body.organization = query.sender  # type: ignore
            query.body.employee_profile = query.recipient  # type: ignore
            query.body.save()  # type: ignore

        return query.body

    Organization.query_handler = query_handler  # type: ignore
