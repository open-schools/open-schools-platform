import typing

from rest_framework.exceptions import NotAcceptable

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.models import StudentProfile


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
    without_body = True
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.CANCELED]
    available_statuses = {
        (Query.Status.SENT, 'parents.parent_profile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, 'families.family_access'): (Query.Status.CANCELED,),
    }

    @typing.no_type_check
    def query_to_parent_profile(self, query: Query):
        if type(query.sender) != Family or type(query.recipient) != ParentProfile:
            raise NotAcceptable("Query is corrupted")
        if query.status == Query.Status.ACCEPTED:
            add_parent_profile_to_family(query.sender, query.recipient)

    change_query = {
        ParentProfile: query_to_parent_profile
    }


setattr(Family, "query_handler", FamilyQueryHandler())
