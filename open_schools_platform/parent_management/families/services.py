import typing

from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from open_schools_platform.common.services import BaseQueryHandler
from open_schools_platform.common.utils import form_ids_string_from_queryset
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.organization_management.organizations.selectors import get_organizations
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.student_management.students.models import StudentProfile, Student
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
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.IN_PROGRESS,
                        Query.Status.CANCELED]
    available_statuses = {
        (Query.Status.SENT, 'parents.parentprofile_access'): (Query.Status.DECLINED, Query.Status.ACCEPTED),
        (Query.Status.SENT, 'families.family_access'): (Query.Status.CANCELED,),
        (Query.Status.IN_PROGRESS, 'families.family_access'): (Query.Status.CANCELED,),
        (Query.Status.SENT, 'organizations.organization_access'): (Query.Status.IN_PROGRESS, Query.Status.CLOSED),
        (Query.Status.IN_PROGRESS, 'organizations.organization_access'): (Query.Status.CLOSED,),
    }

    @typing.no_type_check
    def query_to_parent_profile(self, query: Query):
        if query.status == Query.Status.ACCEPTED:
            add_parent_profile_to_family(query.sender, query.recipient)

    @typing.no_type_check
    def ticket_to_organization(self, query: Query):
        pass

    change_query = {
        ParentProfile: query_to_parent_profile,
        Organization: ticket_to_organization,
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


def get_accessible_students(user: User) -> QuerySet[Student]:
    families = user.parent_profile.families.all()
    student_profiles = get_student_profiles_by_families(families)
    students = get_students(filters={"student_profile": user.student_profile.id})
    for student_profile in student_profiles:
        students |= get_students(filters={"student_profile": student_profile.id})
    return students


def get_accessible_organizations(user: User, filters=None) -> typing.List[Organization]:
    if filters is None:
        filters = {}

    accessible_organizations_str = ','.join(
        set(map(lambda x: str(x.circle.organization.id) if x.circle else "", get_accessible_students(user))))
    filters.update({"ids": accessible_organizations_str})
    organizations = get_organizations(filters=filters, empty_filters=True)
    return list(organizations)


def get_families_that_interact_with_organization(user: User, organization: Organization) -> typing.List[Family]:
    students = get_accessible_students(user).filter(circle__organization=organization).all()
    families = Family.objects.none()
    for student in students:
        if student.student_profile:
            families |= student.student_profile.families.all()
    return list(families)


setattr(Family, "query_handler", FamilyQueryHandler())
