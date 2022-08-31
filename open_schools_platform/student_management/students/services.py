from typing import Dict

from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.exceptions import NotAcceptable, MethodNotAllowed

from open_schools_platform.common.services import model_update, BaseQueryHandler
from open_schools_platform.common.utils import filter_dict_from_none_values
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family, create_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import query_update, create_query
from open_schools_platform.student_management.students.models import StudentProfile, Student, \
    StudentProfileCircleAdditional
from open_schools_platform.student_management.students.serializers import AutoStudentJoinCircleQuerySerializer
from open_schools_platform.user_management.users.models import User


def create_student_profile(name: str, age: int, phone: PhoneNumber = None) -> StudentProfile:
    student_profile = StudentProfile.objects.create_student_profile(
        name=name,
        age=age,
        phone=phone,
    )
    return student_profile


def create_student_profile_circle_query(student_profile: StudentProfile, circle: Circle,
                                        student: Student, additional: StudentProfileCircleAdditional) -> Query:
    return create_query(
        sender_model_name="studentprofile", sender_id=student_profile.id,
        recipient_model_name="circle", recipient_id=circle.id,
        body_model_name="student", body_id=student.id,
        additional_model_name="studentprofilecircleadditional", additional_id=additional.id,
    )


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


def update_student_join_circle_body(*, query: Query, data) -> Query:
    non_side_effect_fields = ['name']
    filtered_data = filter_dict_from_none_values(data)
    if query.body is None:
        raise NotAcceptable
    query.body, has_updated = model_update(
        instance=query.body,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return query


def create_studentprofileicrcle_additional(text: str = None, parent_phone: PhoneNumber = None,
                                           parent_name: str = None, student_phone: PhoneNumber = None)\
        -> StudentProfileCircleAdditional:
    additional = StudentProfileCircleAdditional.objects.create(
        text=text,
        parent_phone=parent_phone,
        parent_name=parent_name,
        student_phone=student_phone,
    )
    return additional


class StudentProfileQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.IN_PROGRESS,
                        Query.Status.CANCELED]

    @staticmethod
    def query_handler(query: Query, new_status: str, user: User):
        BaseQueryHandler.query_handler_checks(StudentProfileQueryHandler, query, new_status, user)

        circle_access = user.has_perm("circles.circle_access", query.recipient)
        student_profile_access = user.has_perm("students.student_profile_access", query.sender)

        if student_profile_access and circle_access:
            pass
        elif student_profile_access:
            if query.status != Query.Status.SENT:
                raise NotAcceptable("Сan no longer change the query")
            if new_status != Query.Status.CANCELED:
                raise NotAcceptable("User can only set canceled status")
        elif circle_access:
            if new_status == Query.Status.CANCELED:
                raise NotAcceptable("Circle cannot cancel query, it can only decline it")
            if query.status == Query.Status.CANCELED:
                raise NotAcceptable("Сan no longer change the query")

        query_update(query=query, data={"status": new_status})
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise MethodNotAllowed("put", detail="Query is corrupted")
            query.body.circle = query.recipient
            query.body.student_profile = query.sender
            query.body.save()

        return query

    setattr(StudentProfile, "query_handler", query_handler)


def autogenerate_family_logic(fields: Dict, user: User) -> StudentProfile:
    student_profile = create_student_profile(
        **fields["student_profile"]
    )
    family = create_family(parent=user.parent_profile)
    add_student_profile_to_family(family=family, student_profile=student_profile)
    return student_profile


def query_creation_logic(fields: Dict, circle: Circle,
                         student_profile: StudentProfile, parent_user: User = None) -> Query:
    student = create_student(name=student_profile.name)
    query = create_query(
        sender_model_name="studentprofile", sender_id=student_profile.id,
        recipient_model_name="circle", recipient_id=circle.id,
        body_model_name="student", body_id=student.id,
    )

    if parent_user:
        additional = create_studentprofileicrcle_additional(
            parent_phone=parent_user.phone,
            parent_name=parent_user.parent_profile.name,
            text=fields["additional"]["text"],
            student_phone=student_profile.phone,
        )
        query.additional_model_name = "studentprofileicrcleadditional"
        query.additional_id = additional.id
        query.additional = additional

    query.save()
    return query
