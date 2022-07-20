from rest_framework.exceptions import NotAcceptable

from open_schools_platform.common.services import model_update
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.selectors import get_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.student_management.student.models import StudentProfile, Student
from open_schools_platform.user_management.users.models import User


def create_student_profile(name: str, age: int) -> StudentProfile:
    student_profile = StudentProfile.objects.create_student_profile(
        name=name,
        age=age,
    )
    return student_profile


def create_student(name: str, circle: Circle = None, student_profile: StudentProfile = None) -> Student:
    student = Student.objects.create_student(
        name=name,
        circle=circle,
        student_profile=student_profile
    )
    return student


def can_user_interact_with_student_profile_check(family: Family, user: User) -> bool:
    # TODO:  think about mypy check hidden attributes made by related_name
    return user.parent_profile in family.parent_profiles.all()


def update_student_profile(*, student_profile: StudentProfile, data) -> StudentProfile:
    non_side_effect_fields = ['age', 'name']
    filtered_data = filter_dict_from_none_values(data)
    student_profile, has_updated = model_update(
        instance=student_profile,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return student_profile


class StudentProfileQueryHandler:
    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        # TODO: Disable some statuses for some models here
        allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.IN_PROGRESS,
                            Query.Status.CANCELED]
        if query.status == new_status:
            return query.body
        if new_status not in allowed_statuses:
            raise NotAcceptable("Please enter a valid status for query")
        if query.sender in get_family(filters={"parent_profiles": user.parent_profile}).student_profiles.all():
            if query.status != Query.Status.SENT:
                raise NotAcceptable("Сan no longer change the query")
            if new_status == Query.Status.DECLINED or Query.Status.ACCEPTED or Query.Status.IN_PROGRESS:
                raise NotAcceptable("User can only set canceled status")
        else:
            if new_status == Query.Status.CANCELED:
                raise NotAcceptable("Circle cannot cancel query, it can only decline it")
        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            query.body.circle = query.recipient  # type: ignore
            query.body.student_profile = query.sender  # type: ignore

        query.body.save()  # type: ignore

        return query.body

    StudentProfile.query_handler = query_handler  # type: ignore
