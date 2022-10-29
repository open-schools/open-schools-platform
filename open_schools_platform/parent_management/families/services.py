from rest_framework.exceptions import NotAcceptable

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User


def add_parent_profile_to_family(family: Family, parent: ParentProfile):
    family.parent_profiles.add(parent)
    family.save()
    return family


def add_student_profile_to_family(family: Family, student_profile: StudentProfile):
    family.student_profiles.add(student_profile)
    family.save()
    return family


def create_family(parent: ParentProfile, name: str = None) -> Family:
    if name is None:
        name = "Family of " + parent.name
    family = Family.objects.create_family(
        name=name,
    )
    add_parent_profile_to_family(family=family, parent=parent)
    return family


class FamilyQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.CANCELED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(FamilyQueryHandler, query, new_status, user, without_body=True)

        family_access = user.has_perm("families.family_access", query.sender)
        parent_profile_access = user.has_perm("parents.parent_profile_access", query.recipient)

        if family_access or family_access and parent_profile_access:
            if query.status != Query.Status.SENT:
                raise NotAcceptable("Сan no longer change the query")
            if new_status != Query.Status.CANCELED:
                raise NotAcceptable("Family can only set canceled status")
        elif parent_profile_access:
            if new_status == Query.Status.CANCELED:
                raise NotAcceptable("Parent profile cannot cancel query, he can only decline or accept it")
            if query.status != Query.Status.SENT:
                raise NotAcceptable("Сan no longer change the query")

        query_update(query=query, data={"status": new_status})
        if type(query.sender) != Family or type(query.recipient) != ParentProfile:
            raise NotAcceptable("Query is corrupted")
        if query.status == Query.Status.ACCEPTED:
            add_parent_profile_to_family(query.sender, query.recipient)

        return query

    setattr(Family, "query_handler", query_handler)
