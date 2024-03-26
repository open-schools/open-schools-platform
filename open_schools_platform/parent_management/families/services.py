import typing

from django.contrib.contenttypes.models import ContentType

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.selectors import get_families
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.query_management.queries.selectors import get_queries
from open_schools_platform.student_management.students.selectors import get_student_profiles_by_families, get_students
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
    without_body = True
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.CANCELED]
    available_statuses = {
        (Query.Status.SENT, 'parents.parent_profile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, 'families.family_access'): (Query.Status.CANCELED,),
    }

    @typing.no_type_check
    def query_to_parent_profile(self, query: Query):
        if query.status == Query.Status.ACCEPTED:
            add_parent_profile_to_family(query.sender, query.recipient)

    change_query = {
        ParentProfile: query_to_parent_profile
    }


def get_all_student_invites_for_current_user_families(user: User):
    return get_queries(
        filters={
            "sender_ct": ContentType.objects.get(model="circle"),
            "recipient_ct": ContentType.objects.get(model="family"),
            "body_ct": ContentType.objects.get(model="student"),
            "additional_ct": ContentType.objects.get(model="studentprofile"),
            "recipient_ids": form_ids_string_from_queryset(user.parent_profile.families.all())
        }
    )


def get_accessible_organizations(user: User) -> typing.List[Organization]:
    families = get_families(
        filters={"parent_profiles": str(user.parent_profile.id)},
    )
    student_profiles = get_student_profiles_by_families(families)
    students = get_students(filters={"student_profile": user.student_profile.id})
    for student_profile in student_profiles:
        students |= get_students(filters={"student_profile": student_profile.id})

    return list(set(map(lambda x: x.circle.organization, students)))


setattr(Family, "query_handler", FamilyQueryHandler())
