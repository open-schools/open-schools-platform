from rest_framework.exceptions import ValidationError, MethodNotAllowed

from open_schools_platform.common.services import BaseQueryHandler
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


class OrganizationQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.SENT, Query.Status.CANCELED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(OrganizationQueryHandler, query, new_status, user)

        from open_schools_platform.organization_management.employees.models import EmployeeProfile

        if type(query.recipient) is not EmployeeProfile:
            raise ValidationError(detail="The recipient must be an Employee if the sender is an organization")

        # TODO: think about type: ignore lines -

        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise MethodNotAllowed("put", detail="Query is corrupted")
            query.body.organization = query.sender
            query.body.employee_profile = query.recipient
            query.body.save()

        return query

    Organization.query_handler = query_handler
