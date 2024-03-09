import typing
import uuid
from typing import Dict

from django.core.exceptions import BadRequest
from django.db.models import QuerySet
from phonenumber_field.phonenumber import PhoneNumber

from open_schools_platform.common.services import model_update, BaseQueryHandler
from open_schools_platform.common.utils import filter_dict_from_none_values, form_ids_string_from_queryset
from open_schools_platform.errors.exceptions import QueryCorrupted
from open_schools_platform.organization_management.circles.models import Circle
from open_schools_platform.student_management.students.exports import StudentExport
from open_schools_platform.parent_management.families.models import Family
from open_schools_platform.parent_management.families.services import add_student_profile_to_family, create_family
from open_schools_platform.query_management.queries.models import Query
from open_schools_platform.query_management.queries.services import create_query
from open_schools_platform.student_management.students.models import StudentProfile, Student, \
    StudentProfileCircleAdditional
from open_schools_platform.student_management.students.selectors import get_student_profiles
from open_schools_platform.user_management.users.models import User


def create_student_profile(name: str, age: int = None, user: User = None,
                           phone: PhoneNumber = None, photo: uuid.UUID = None) -> StudentProfile:
    student_profile = StudentProfile.objects.create_student_profile(
        name=name,
        age=age,
        phone=phone,
        photo=photo,
        user=user
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
    non_side_effect_fields = ['age', 'name', 'phone', 'photo']
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
        raise QueryCorrupted
    query.body, has_updated = model_update(
        instance=query.body,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return query


def create_student_profile_circle_additional(text: str = None, parent_phone: PhoneNumber = None,
                                             parent_name: str = None, student_phone: PhoneNumber = None) \
        -> StudentProfileCircleAdditional:
    additional = StudentProfileCircleAdditional.objects.create(
        text=text,
        parent_phone=parent_phone,
        parent_name=parent_name,
        student_phone=student_phone,
    )
    return additional


def get_student_profile_by_family_or_create_new(student_phone: PhoneNumber, student_name: str,
                                                families: QuerySet[Family]):
    student_profile = get_student_profiles(
        filters={"phone": student_phone,
                 "families": form_ids_string_from_queryset(families)},
        empty_filters=True,
    ).first()

    if not student_profile:
        student_profile = create_student_profile(name=student_name, phone=student_phone)
        first_family = families.first()
        if first_family is None:
            raise BadRequest
        add_student_profile_to_family(family=first_family, student_profile=student_profile)

    return student_profile


class StudentProfileQueryHandler(BaseQueryHandler):
    allowed_statuses = [Query.Status.ACCEPTED, Query.Status.DECLINED, Query.Status.SENT, Query.Status.IN_PROGRESS,
                        Query.Status.CANCELED]
    available_statuses = {
        (Query.Status.SENT, 'circles.circle_access'): (
            Query.Status.DECLINED, Query.Status.IN_PROGRESS, Query.Status.ACCEPTED
        ),
        (Query.Status.IN_PROGRESS, 'circles.circle_access'): (
            Query.Status.DECLINED, Query.Status.ACCEPTED
        ),
        (Query.Status.SENT, 'students.student_profile_access'): (Query.Status.CANCELED,),
    }

    @typing.no_type_check
    def query_to_circle(self, query: Query):
        if query.status == Query.Status.ACCEPTED:
            if query.body is None:
                raise QueryCorrupted()
            query.body.circle = query.recipient
            query.body.student_profile = query.sender
            query.body.save()

    change_query = {
        Circle: query_to_circle
    }


setattr(StudentProfile, "query_handler", StudentProfileQueryHandler())


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
        additional = create_student_profile_circle_additional(
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


def export_students(students: QuerySet, export_format: str):
    data = StudentExport().export(students)
    file = data.export(export_format)
    return file


def update_student(*, student: Student, data) -> Student:
    non_side_effect_fields = ['name']
    filtered_data = filter_dict_from_none_values(data)
    student, has_updated = model_update(
        instance=student,
        fields=non_side_effect_fields,
        data=filtered_data
    )
    return student
