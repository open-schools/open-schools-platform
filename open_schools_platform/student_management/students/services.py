from rest_framework.exceptions import NotAcceptable, MethodNotAllowed

from open_schools_platform.common.services import model_update, BaseQueryHandler
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update
from open_schools_platform.student_management.students.models import StudentProfile, Student
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


class StudentProfileQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.IN_PROGRESS,
                        Query.Status.CANCELED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(StudentProfileQueryHandler, query, new_status, user)

        circle_access = user.has_perm("circles.circle_access", query.recipient)
        student_profile_access = user.has_perm("students.student_profile_access", query.sender)

        if not circle_access:
            if query.status != Query.Status.SENT:
                raise NotAcceptable("Сan no longer change the query")
            if new_status != Query.Status.CANCELED:
                raise NotAcceptable("User can only set canceled status")
        elif not student_profile_access:
            if new_status == Query.Status.CANCELED:
                raise NotAcceptable("Circle cannot cancel query, it can only decline it")

        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise MethodNotAllowed("put", detail="Query is corrupted")
            query.body.circle = query.recipient
            query.body.student_profile = query.sender
            query.body.save()

        return query

    StudentProfile.query_handler = query_handler
